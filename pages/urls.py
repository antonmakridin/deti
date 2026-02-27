from django.urls import path, re_path
from . import views

app_name = 'pages'

urlpatterns = [
    path('', views.home, name='home'),
    re_path(r'^(?P<path>[\w/-]+)/$', views.page_detail_by_path, name='page_detail_by_path'),
    path('<slug:slug>/', views.page_detail, name='page_detail'),
]