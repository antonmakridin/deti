from django.shortcuts import render, get_object_or_404
from .models import Album

def album_list(request):
    albums = Album.objects.filter(is_published=True)
    return render(request, 'gallery/album_list.html', {'albums': albums})

def album_detail(request, slug):
    album = get_object_or_404(Album, slug=slug, is_published=True)
    return render(request, 'gallery/album_detail.html', {'album': album})