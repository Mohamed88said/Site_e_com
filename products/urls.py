from django.urls import path
from . import views

app_name = 'products'

urlpatterns = [
    path('', views.product_list, name='list'),
    path('category/<int:pk>/', views.product_list_by_category, name='category'),
    path('search/', views.product_search, name='search'),
    path('my/', views.my_products, name='my_products'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/', views.product_detail, name='detail'),
    path('<int:pk>/edit/', views.product_edit, name='edit'),
    path('<int:pk>/delete/', views.product_delete, name='delete'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/add/<int:pk>/', views.add_to_wishlist, name='add_to_wishlist'),
    path('wishlist/remove/<int:pk>/', views.remove_from_wishlist, name='remove_from_wishlist'),
    path('compare/', views.compare_products, name='compare'),
    path('<int:pk>/report/', views.report_product, name='report'),
    path('<int:pk>/ask/', views.ask_question, name='ask_question'),
    path('vendor/<int:user_id>/', views.vendor_profile, name='vendor_profile'),
    path('create/', views.product_create, name='create'),
    path('<int:pk>/promo/', views.add_promotion, name='add_promotion'),
    path('dashboard/', views.seller_dashboard, name='seller_dashboard'),
    path('<int:pk>/like_review/', views.like_review, name='like_review'),
    path('question/<int:pk>/like/', views.like_question, name='like_question'),
    path('question/<int:pk>/best/', views.mark_best_answer, name='mark_best_answer'),
    path('<int:pk>/all_reviews/', views.all_reviews, name='all_reviews'),
    path('export_catalogue/', views.export_catalogue_csv, name='export_catalogue'),
    path('import_catalogue/', views.import_catalogue, name='import_catalogue'),
    path('create_bundle/', views.create_bundle, name='create_bundle'),
    path('compare/', views.compare_products, name='compare_products'),
    path('wishlist/', views.wishlist, name='wishlist'),
    path('wishlist/public/<slug:slug>/', views.public_wishlist, name='public_wishlist'),
    path('export/csv/', views.export_csv, name='export_csv'),
    path('export/pdf/', views.export_pdf, name='export_pdf'),
]