from django.contrib import admin
from .models import Banner

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'position', 'order', 'is_active', 'is_current', 'start_date', 'end_date']
    list_filter = ['position', 'is_active', 'start_date', 'end_date']
    list_editable = ['order', 'is_active']
    search_fields = ['title']
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'image', 'link', 'link_text')
        }),
        ('Настройки отображения', {
            'fields': ('position', 'order', 'is_active', 'start_date', 'end_date')
        }),
    )