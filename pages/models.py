from django.db import models
from django.urls import reverse
from mptt.models import MPTTModel, TreeForeignKey
from django.utils.text import slugify
from ckeditor.fields import RichTextField
from documents.models import Document
import re


class Page(MPTTModel):
    title = models.CharField(max_length=255, verbose_name='Название страницы')
    slug = models.SlugField(
        max_length=255, 
        verbose_name='URL',
        blank=True,
        unique=True,
        help_text='URL страницы (генерируется автоматически)'
    )
    content = RichTextField(verbose_name='Содержание', blank=True)
    parent = TreeForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Родительская страница',
        related_name='children'
    )
    order = models.IntegerField(default=0, verbose_name='Порядок')
    is_active = models.BooleanField(default=True, verbose_name='Активна')
    show_in_menu = models.BooleanField(default=True, verbose_name='Показывать в меню')
    meta_title = models.CharField(max_length=255, verbose_name='Meta title', blank=True)
    meta_description = models.TextField(verbose_name='Meta description', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')
    
    class MPTTMeta:
        order_insertion_by = ['order', 'title']
    
    class Meta:
        verbose_name = 'Страница'
        verbose_name_plural = 'Страницы'
        ordering = ['tree_id', 'lft']
    
    def __str__(self):
        return self.title
    
    def get_absolute_url(self):
        # Абсолютный урл с полным путем
        full_path = self.get_full_url()
        return f"/{full_path}/"
    
    def get_full_url(self):
        # Полный урл страницы с учетом вложенности
        if self.parent:
            return f"{self.parent.get_full_url()}/{self.slug}"
        return self.slug
    
    def get_ancestors_ids(self):
        #  Получить список ID всех родителей страницы
        return [ancestor.id for ancestor in self.get_ancestors()]
    
    def get_root(self):
        # Получить корневую страницу для текущей страницы"""
        if self.is_root_node():
            return self
        ancestors = self.get_ancestors()
        if ancestors:
            return ancestors[0]
        return self
    
    def clean(self):
        # Валидация уникальности урла в родительской папке
        from django.core.exceptions import ValidationError
        
        if self.parent:
            siblings = Page.objects.filter(parent=self.parent, slug=self.slug)
            if self.pk:
                siblings = siblings.exclude(pk=self.pk)
            if siblings.exists():
                raise ValidationError({
                    'slug': 'Страница с таким URL уже существует в этом разделе'
                })
        else:
            # Для корневых страниц проверяем уникальность
            roots = Page.objects.filter(parent__isnull=True, slug=self.slug)
            if self.pk:
                roots = roots.exclude(pk=self.pk)
            if roots.exists():
                raise ValidationError({
                    'slug': 'Страница с таким URL уже существует'
                })
    
    def get_processed_content(self):
        # Делаем удобный возврат контента с обработанными ссылками на страницы вида [[page:ID]]
        if not self.content:
            return ""
        
        # Обработка [[page:ID]]
        page_pattern1 = r'\[\[page:(\d+)\]\]'
        # Обработка [[page:ID|текст ссылки]]
        page_pattern2 = r'\[\[page:(\d+)\|([^\]]+)\]\]'

        # Обработка [[document:ID]]
        doc_pattern1 = r'\[\[document:(\d+)\]\]'
        # Обработка [[document:ID|название документа]]
        doc_pattern2 = r'\[\[document:(\d+)\|([^\]]+)\]\]'
        
        def replace_page_link(match):
            page_id = match.group(1)
            link_text = match.group(2) if len(match.groups()) > 1 else None
            
            try:
                linked_page = Page.objects.get(id=page_id, is_active=True)
                text = link_text if link_text else linked_page.title
                return f'<a href="{linked_page.get_absolute_url()}">{text}</a>'
            except Page.DoesNotExist:
                return ""
            
        
        def replace_document_link(match):
            doc_id = match.group(1)
            link_text = match.group(2) if len(match.groups()) > 1 else None
            
            try:
                document = Document.objects.get(id=doc_id, is_active=True)
                text = link_text if link_text else document.title
                return f'<a href="{document.get_absolute_url()}">{text}</a>'
            except Document.DoesNotExist:
                return ""
        
        # Обрабатываем форматы
        content = self.content
        content = re.sub(page_pattern1, replace_page_link, content)
        content = re.sub(page_pattern2, replace_page_link, content)
        content = re.sub(doc_pattern1, replace_document_link, content)
        content = re.sub(doc_pattern2, replace_document_link, content)
        
        return content
    
    def save(self, *args, **kwargs):
        # Автогенерация урла если не указан
        if not self.slug:
            base_slug = slugify(self.title)
            slugs = Page.objects.values_list('slug', flat=True)
            
            slug = base_slug
            counter = 1
            while slug in slugs:
                slug = f"{base_slug}-{counter}"
                counter += 1
                
            self.slug = slug
                
        super().save(*args, **kwargs)
    
    def get_menu_items(self):
        # Получить все дочерние страницы для меню
        return self.get_children().filter(show_in_menu=True, is_active=True)

    @classmethod
    def get_root_pages(cls):
        # Получить корневые страницы для меню
        return cls.objects.filter(parent__isnull=True, show_in_menu=True, is_active=True)