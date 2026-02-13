from django.shortcuts import render, get_object_or_404
from django.http import Http404
from news.models import News
from .models import Page

def home(request):
    latest_news = News.objects.filter(is_published=True).order_by('-published_date')[:3]
    context = {
        'latest_news': latest_news
    }
    return render(request, 'pages/home.html', context)

def page_detail(request, slug):
    page = get_object_or_404(Page, slug=slug, is_active=True)
    return render(request, 'pages/page_detail.html', {'page': page})

def page_detail_by_path(request, path):
    # Разделяем путь на части
    path_parts = path.strip('/').split('/')
    
    # Находим страницу по полному пути
    current_page = None
    
    for slug in path_parts:
        if current_page is None:
            # Ищем корневую страницу
            current_page = get_object_or_404(
                Page, 
                slug=slug, 
                parent__isnull=True, 
                is_active=True
            )
        else:
            # Ищем дочернюю страницу
            current_page = get_object_or_404(
                Page, 
                slug=slug, 
                parent=current_page, 
                is_active=True
            )
    
    return render(request, 'pages/page_detail.html', {'page': current_page})