from django.contrib import admin
from .models import Payment

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('order', 'user', 'amount', 'method', 'status', 'payment_date')
    list_filter = ('status', 'method')
    search_fields = ('order__id', 'user__username', 'transaction_id')