from django.contrib import admin
from .models import User, SellerProfile, DeliveryProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'is_verified')
    search_fields = ('username', 'email', 'role')

@admin.register(SellerProfile)
class SellerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'shop_name', 'rating')

@admin.register(DeliveryProfile)
class DeliveryProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'available')