from django.contrib import admin
from .models import Album, GalleryImage

class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 1

@admin.register(Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'is_published', 'created_at']
    list_filter = ['is_published', 'created_at']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [GalleryImageInline]