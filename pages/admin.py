from django.contrib import admin
from django.utils.html import format_html
from mptt.admin import MPTTModelAdmin
from django.contrib.admin.templatetags.admin_urls import admin_urlname
from django.template.defaultfilters import urlencode
from django.utils.safestring import mark_safe
from .models import Page

@admin.register(Page)
class PageAdmin(MPTTModelAdmin):
    list_display = ['title_with_toggle', 'slug', 'parent', 'order', 'is_active', 'show_in_menu', 'get_full_url_display', 'created_at']
    list_display_links = ['title_with_toggle']
    list_filter = ['is_active', 'show_in_menu', 'parent', 'created_at']
    list_editable = ['order', 'is_active', 'show_in_menu']
    search_fields = ['title', 'content', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ['created_at', 'updated_at']
    
    # Настройки для свернутых элементов
    expand_tree_by_default = False
    
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'slug', 'content', 'parent', 'order', 'is_active', 'show_in_menu')
        }),
        ('SEO настройки', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def title_with_toggle(self, obj):
        # Отображение заголовка с кнопкой свернуть/развернуть
        level = getattr(obj, 'level', 0)
        has_children = obj.get_children().exists()
        
        toggle = ''
        if has_children:
            toggle = f'<span class="tree-toggle" data-page-id="{obj.id}" style="cursor: pointer; margin-right: 5px;">▶</span>'
        
        indent = '&nbsp;&nbsp;&nbsp;&nbsp;' * level
        title = f'{indent}{toggle}{obj.title}'
        
        return mark_safe(title)
    title_with_toggle.short_description = 'Название'
    
    def get_full_url_display(self, obj):
        return format_html('<code>/pages/{}</code>', obj.get_full_url())
    get_full_url_display.short_description = 'Полный URL'
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('tree_id', 'lft')
    
    class Media:
        js = ('admin/js/pages_tree.js',)