from django.db import models

class Album(models.Model):
    title = models.CharField(max_length=200, verbose_name='Название')
    slug = models.SlugField(unique=True, verbose_name='URL')
    description = models.TextField(blank=True, verbose_name='Описание')
    cover = models.ImageField(upload_to='gallery/covers/', verbose_name='Обложка')
    is_published = models.BooleanField(default=True, verbose_name='Опубликовано')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')

    class Meta:
        verbose_name = 'Альбом'
        verbose_name_plural = 'Альбомы'

    def __str__(self):
        return self.title

class GalleryImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='gallery/images/', verbose_name='Изображение')
    title = models.CharField(max_length=200, blank=True, verbose_name='Название')
    description = models.TextField(blank=True, verbose_name='Описание')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создано')

    class Meta:
        verbose_name = 'Изображение галереи'
        verbose_name_plural = 'Изображения галереи'
        ordering = ['order']

    def __str__(self):
        return self.title if self.title else f"Image {self.id}"