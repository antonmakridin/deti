from .models import Page

def menu_pages(request):
    menu_pages = Page.get_root_pages()
    return {
        'menu_pages': menu_pages
    }