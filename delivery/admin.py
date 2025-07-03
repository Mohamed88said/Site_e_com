from django.contrib import admin
from .models import Delivery

@admin.register(Delivery)
class DeliveryAdmin(admin.ModelAdmin):
    list_display = ('order', 'delivery_person', 'status', 'assigned_at', 'delivered_at')
    list_filter = ('status',)
    search_fields = ('order__id', 'delivery_person__username')