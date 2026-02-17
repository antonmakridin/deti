from django.db import models
from django.utils import timezone
from django.urls import reverse
import hashlib
import time
import os


def document_upload_path(instance, filename):
    # Генерим путь для загрузки файла вида documents/год/месяц/хэш_имя
    
    ext = os.path.splitext(filename)[1].lower()
    hash_input = f"{time.time()}{filename}".encode('utf-8')
    hash_name = hashlib.sha256(hash_input).hexdigest()[:20]

    return os.path.join(
        'documents',
        timezone.now().strftime('%Y/%m'),
        f"{hash_name}{ext}"
    )


class Document(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название документа'
    )
    file = models.FileField(
        upload_to=document_upload_path,
        verbose_name='Файл'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата загрузки'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )
    download_count = models.PositiveIntegerField(
        default=0,
        verbose_name='Количество скачиваний',
        editable=False
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активен'
    )
    order = models.IntegerField(
        default=0,
        verbose_name='Порядок сортировки'
    )
    
    class Meta:
        verbose_name = 'Документ'
        verbose_name_plural = 'Документы'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def increment_download_count(self):
        # Инкремент счетчика скачиваний
        self.download_count += 1
        self.save(update_fields=['download_count'])
    
    def get_file_size(self):
        # Вывод размера файла
        if self.file and hasattr(self.file, 'size'):
            size = self.file.size
            for unit in ['Б', 'КБ', 'МБ', 'ГБ']:
                if size < 1024.0:
                    return f"{size:.1f} {unit}"
                size /= 1024.0
        return "0 Б"
    
    def get_file_extension(self):
        # Вывод расширения файла
        if self.file:
            return os.path.splitext(self.file.name)[1].lower().replace('.', '').upper()
        return ''
    
    def get_original_filename(self):
        # Вывод оригинального имени файла для скачивания
        if self.file:
            # Получаем расширение
            ext = os.path.splitext(self.file.name)[1]
            # Создаем безопасное имя для скачивания из поля title
            safe_title = "".join(c for c in self.title if c.isalnum() or c in (' ', '-', '_')).rstrip()
            return f"{safe_title}{ext}"
        return ''
    
    def get_absolute_url(self):
        # Вывод УРЛ для скачивания документа
        return reverse('documents:download', args=[self.pk])