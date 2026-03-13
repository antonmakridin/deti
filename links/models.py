from django.db import models
from django.utils import timezone

class Links(models.Model):
    POSITION_CHOICES = [
        ('main', 'Главная страница'),
    ]
    
    title = models.CharField(max_length=200, verbose_name='Заголовок')
    image = models.ImageField(upload_to='links/', verbose_name='Изображение')
    link = models.URLField(blank=True, null=True, verbose_name='Ссылка')
    link_text = models.CharField(max_length=100, verbose_name='Текст кнопки')
    
    position = models.CharField(max_length=20, choices=POSITION_CHOICES, default='main', verbose_name='Позиция')
    order = models.PositiveIntegerField(default=0, verbose_name='Порядок')
    
    is_active = models.BooleanField(default=True, verbose_name='Активен')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Создан')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Обновлен')
    
    # дата начала и окончания показа
    start_date = models.DateTimeField(default=timezone.now, verbose_name='Дата начала показа')
    end_date = models.DateTimeField(blank=True, null=True, verbose_name='Дата окончания показа')
    
    class Meta:
        verbose_name = 'Ссылка'
        verbose_name_plural = 'Ссылки'
        ordering = ['order', '-created_at']
    
    def __str__(self):
        return self.title
    
    def is_current(self):
        # проверка активности ссылки
        now = timezone.now()
        if self.start_date > now:
            return False
        if self.end_date and self.end_date < now:
            return False
        return True
    is_current.boolean = True
    is_current.short_description = 'Текущий'