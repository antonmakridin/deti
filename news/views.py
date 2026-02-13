from django.shortcuts import render, get_object_or_404
from .models import News

def news_list(request):
    category = request.GET.get('category', '')
    news_list = News.objects.filter(is_published=True)
    
    if category:
        news_list = news_list.filter(category=category)
    
    news_list = news_list.order_by('-published_date')
    
    context = {
        'news_list': news_list,
        'current_category': category,
    }
    return render(request, 'news/news_list.html', context)

def news_detail(request, slug):
    news = get_object_or_404(News, slug=slug, is_published=True)
    
    # Последние 5 новостей для списка последних новостей сбоку
    latest_news_list = News.objects.filter(is_published=True).exclude(id=news.id).order_by('-published_date')[:5]
    
    # Похожие новости (той же категории)
    related_news_list = News.objects.filter(
        category=news.category, 
        is_published=True
    ).exclude(id=news.id).order_by('-published_date')[:4]
    
    context = {
        'news': news,
        'latest_news_list': latest_news_list,
        'related_news_list': related_news_list,
    }
    return render(request, 'news/news_detail.html', context)