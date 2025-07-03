from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    path('', views.payment_list, name='list'),
    path('<int:pk>/', views.payment_detail, name='detail'),
    path('create/<int:order_id>/', views.payment_create, name='create'),
    path('export/csv/', views.export_payments_csv, name='export_csv'),
    path('export/pdf/', views.export_payments_pdf, name='export_pdf'),
]