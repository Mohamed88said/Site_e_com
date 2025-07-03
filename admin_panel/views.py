from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from accounts.models import User
from products.models import Product
from orders.models import Order
from payments.models import Payment
from returns.models import ReturnRequest
from delivery.models import Delivery

@staff_member_required
def dashboard(request):
    nb_users = User.objects.count()
    nb_sellers = User.objects.filter(role='seller').count()
    nb_buyers = User.objects.filter(role='buyer').count()
    nb_products = Product.objects.count()
    nb_orders = Order.objects.count()
    nb_payments = Payment.objects.count()
    nb_returns = ReturnRequest.objects.count()
    nb_deliveries = Delivery.objects.count()

    return render(request, 'admin_panel/dashboard.html', {
        'nb_users': nb_users,
        'nb_sellers': nb_sellers,
        'nb_buyers': nb_buyers,
        'nb_products': nb_products,
        'nb_orders': nb_orders,
        'nb_payments': nb_payments,
        'nb_returns': nb_returns,
        'nb_deliveries': nb_deliveries,
    })