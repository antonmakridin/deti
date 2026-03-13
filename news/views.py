from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import News

def news_list(request):
    category = request.GET.get('category', '')
    news_list = News.objects.filter(is_published=True)
    
    if category:
        news_list = news_list.filter(category=category)
    
    news_list = news_list.order_by('-published_date')
    
    # пагинация
    paginator = Paginator(news_list, 6) # колво новостей на страницу
    page = request.GET.get('page')
    
    # проверки
    try:
        news = paginator.page(page)
    except PageNotAnInteger:
        news = paginator.page(1)
    except EmptyPage:
        news = paginator.page(paginator.num_pages)
    
    context = {
        'news_list': news,
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