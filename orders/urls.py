from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    path('', views.order_list, name='list'),
    path('<int:pk>/', views.order_detail, name='detail'),
    path('create/<int:product_id>/', views.order_create, name='create'),
    path('checkout/<int:pk>/', views.order_checkout, name='checkout'),
    path('seller/dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('historique/', views.order_history, name='order_history'),
    path('export/csv/', views.export_orders_csv, name='export_csv'),
    path('export/pdf/', views.export_orders_pdf, name='export_pdf'),
    path('facture/<int:pk>/', views.invoice_pdf, name='invoice_pdf'),
]