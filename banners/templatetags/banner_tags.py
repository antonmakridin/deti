from django import template
from django.utils import timezone
from ..models import Banner

register = template.Library()

@register.inclusion_tag('banners/banners_main.html')
def show_main_banners(limit=3):
    # Вывод баннеров на главной странице
    banners = Banner.objects.filter(
        is_active=True, 
        position='main'
    ).filter(
        start_date__lte=timezone.now()
    ).exclude(
        end_date__lt=timezone.now()
    )[:limit]
    
    return {'banners': banners}

@register.inclusion_tag('banners/banners_left.html')
def show_left_banners(limit=3):
    # Вывод баннеров на главной странице
    banners = Banner.objects.filter(
        is_active=True, 
        position='main'
    ).filter(
        start_date__lte=timezone.now()
    ).exclude(
        end_date__lt=timezone.now()
    )[:limit]
    
    return {'banners': banners}