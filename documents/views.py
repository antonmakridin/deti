from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404
from django.contrib.contenttypes.models import ContentType
from urllib.parse import quote
from .models import Document


def download_document(request, document_id):
    # ссылка для скачивания со счетчиком скачиваний

    document = get_object_or_404(Document, id=document_id, is_active=True)
    
    if not document.file:
        raise Http404("Файл не найден")
    
    # Увеличиваем счетчик скачиваний
    document.increment_download_count()
    
    # Открываем файл для чтения
    file_handle = document.file.open('rb')
    
    # Создаем response с файлом
    response = FileResponse(file_handle)
    
    # Получаем имя для скачивания из поля title
    download_name = document.get_original_filename()
    
    # Кодируем имя файла для корректной обработки браузерами
    encoded_filename = quote(download_name)
    
    # Устанавливаем заголовки для правильного имени файла при скачивании
    response['Content-Disposition'] = f'attachment; filename="{encoded_filename}"; filename*=UTF-8\'\'{encoded_filename}'
    
    # Определяем Content-Type на основе расширения файла
    ext = document.get_file_extension().lower()
    content_types = {
        'pdf': 'application/pdf',
        'doc': 'application/msword',
        'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'odt': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'xls': 'application/vnd.ms-excel',
        'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'ods': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        'jpg': 'image/jpeg',
        'jpeg': 'image/jpeg',
        'png': 'image/png',
        'gif': 'image/gif',
        'txt': 'text/plain',
        'zip': 'application/zip',
        'rar': 'application/x-rar-compressed',
    }
    response['Content-Type'] = content_types.get(ext, 'application/octet-stream')
    
    return response