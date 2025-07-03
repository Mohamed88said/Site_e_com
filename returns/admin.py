from django.contrib import admin
from .models import ReturnRequest

@admin.register(ReturnRequest)
class ReturnRequestAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'status', 'created_at', 'processed_at')
    list_filter = ('status',)
    search_fields = ('order__id', 'user__username')