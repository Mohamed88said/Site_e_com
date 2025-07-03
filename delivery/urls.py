from django.urls import path
from . import views

app_name = 'delivery'

urlpatterns = [
    path('dashboard/', views.delivery_dashboard, name='dashboard'),
    path('', views.delivery_list, name='list'),
    path('<int:pk>/', views.delivery_detail, name='detail'),
    path('start/<int:pk>/', views.start_delivery, name='start'),
    path('mark_delivered/<int:pk>/', views.mark_delivered, name='mark_delivered'),
    path('<int:pk>/update_position/', views.update_position, name='update_position'),
    path('historique/', views.delivery_history, name='delivery_history'),
    path('<int:pk>/qr/', views.delivery_qr, name='qr'),
    path('scan/<str:qr_token>/', views.scan_qr, name='scan_qr'),
]