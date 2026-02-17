from django.contrib import admin
from django.utils.html import format_html
from .models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = (
        'title', 
        'id',
        'file_info', 
        'created_at', 
        'updated_at', 
        'download_count', 
        'is_active',
        'order'
    )
    list_filter = ('is_active', 'created_at')
    search_fields = ('title',)
    list_editable = ('order', 'is_active')
    readonly_fields = ('created_at', 'updated_at', 'download_count', 'file_preview')
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'file', 'file_preview')
        }),
        ('Дополнительно', {
            'fields': ('order', 'is_active')
        }),
        ('Автоматические поля', {
            'fields': ('created_at', 'updated_at', 'download_count'),
            'classes': ('collapse',)
        }),
    )
    
    def file_info(self, obj):
        # Информация о файле в списке
        if obj.file:
            return format_html(
                '{}<br><small>{} | {}</small>',
                obj.get_file_extension(),
                obj.get_file_size(),
                obj.file.name.split('/')[-1]
            )
        return "-"
    file_info.short_description = 'Файл'
    
    def file_preview(self, obj):
        # Предпросмотр файла в админке
        if obj.file:
            ext = obj.get_file_extension().lower()
            if ext in ['jpg', 'jpeg', 'png', 'gif', 'svg']:
                return format_html(
                    '<img src="{}" style="max-height: 200px; max-width: 100%;" />',
                    obj.file.url
                )
            elif ext in ['pdf']:
                return format_html(
                    '<a href="{}" target="_blank">Просмотреть PDF</a>',
                    obj.file.url
                )
            else:
                return format_html(
                    '<a href="{}" target="_blank">Скачать файл</a>',
                    obj.file.url
                )
        return "-"
    file_preview.short_description = 'Предпросмотр'