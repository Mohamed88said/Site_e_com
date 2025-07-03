from django.urls import path
from . import views

app_name = 'returns'

urlpatterns = [
    path('', views.returns_list, name='list'),
    path('<int:pk>/', views.return_detail, name='detail'),
    path('new/<int:order_id>/', views.return_create, name='create'),
    path('process/<int:pk>/', views.return_process, name='process'),
    path('export/csv/', views.export_returns_csv, name='export_csv'),
    path('export/pdf/', views.export_returns_pdf, name='export_pdf'),
]