from django.db import models
from ckeditor.fields import RichTextField
from documents.models import Document
from pages.models import Page
import re

class NewsCategory(models.Model):
    name = models.CharField(max_length=100, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    class Meta:
        verbose_name = 'Категория новостей'
        verbose_name_plural = 'Категории новостей'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name

class News(models.Model):
    CATEGORY_CHOICES = [
        ('news', 'Новости'),
        ('announcements', 'Анонсы'),
        ('interesting', 'Интересно'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    slug = models.SlugField(unique=True, verbose_name='URL')
    content = RichTextField(verbose_name='Содержание')
    excerpt = models.TextField(max_length=500, blank=True, null=True, verbose_name='Краткое описание')
    image = models.ImageField(upload_to='news/', blank=True, null=True, verbose_name='Изображение')
    category = models.CharField(
        max_length=20, 
        choices=CATEGORY_CHOICES, 
        default='news', 
        verbose_name='Категория'
    )
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    published_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата публикации')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создана')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлена')

    
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

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:news_detail', kwargs={'slug': self.slug})