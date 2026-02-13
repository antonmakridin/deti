from django.contrib import admin
from .models import News, NewsCategory

@admin.register(NewsCategory)
class NewsCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'order']
    list_editable = ['order']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(News)
class NewsAdmin(admin.ModelAdmin):
    list_display = ['title', 'slug', 'category', 'is_published', 'published_date']
    list_filter = ['category', 'is_published', 'published_date']
    list_editable = ['is_published']
    search_fields = ['title', 'content', 'excerpt']
    prepopulated_fields = {'slug': ('title',)}
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'excerpt', 'image', 'category')
        }),
        ('Настройки', {
            'fields': ('is_published',)
        }),
    )