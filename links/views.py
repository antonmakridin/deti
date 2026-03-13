from django.shortcuts import render
from .models import Links

def links_list(request):
    linkses = Links.objects.filter(is_active=True)
    context = {
        'linkses': linkses,
    }
    return render(request, 'links/links.html', context)