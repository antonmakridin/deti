from django import template
from django.utils import timezone
from ..models import Links

register = template.Library()

@register.inclusion_tag('links/links.html')
def show_main_links():
    # Вывод ссылок
    linkses = Links.objects.filter(
        is_active=True, 
        position='main'
    ).filter(
        start_date__lte=timezone.now()
    ).exclude(
        end_date__lt=timezone.now()
    )
    
    return {'linkses': linkses}