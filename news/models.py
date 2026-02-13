from django.db import models
from ckeditor.fields import RichTextField

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

    class Meta:
        verbose_name = 'Новость'
        verbose_name_plural = 'Новости'
        ordering = ['-published_date']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('news:news_detail', kwargs={'slug': self.slug})