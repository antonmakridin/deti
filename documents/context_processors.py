from .models import Document

def all_documents(request):
    return {
        'all_documents': Document.objects.filter(is_active=True).order_by('order', '-created_at')
    }