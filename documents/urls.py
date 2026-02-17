from django.urls import path
from . import views

app_name = 'documents'

urlpatterns = [
    path('download/<int:document_id>/', views.download_document, name='download'),
]