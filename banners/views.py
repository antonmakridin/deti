from django.shortcuts import render
from .models import Banner

def banner_list(request):
    banners = Banner.objects.filter(is_active=True)
    context = {
        'banners': banners,
    }
    return render(request, 'banners/banner_list.html', context)