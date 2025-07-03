from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from products.models import Product
from .models import Order, OrderItem
from .forms import OrderCreateForm, CheckoutForm
from django.contrib import messages
from payments.models import Payment
from delivery.models import Delivery
from notifications.utils import notify_user

@login_required
def order_list(request):
    if request.user.role == 'buyer':
        orders = Order.objects.filter(buyer=request.user)
    elif request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user)
    else:
        orders = Order.objects.none()
    return render(request, 'orders/order_list.html', {'orders': orders})

@login_required
def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if (request.user != order.buyer and request.user != order.seller):
        return redirect('orders:list')
    return render(request, 'orders/order_detail.html', {'order': order})


@login_required
def order_create(request, product_id):
    product = get_object_or_404(Product, pk=product_id, is_active=True)
    if request.user.role != 'buyer':
        return redirect('products:detail', pk=product_id)
    if request.method == 'POST':
        form = OrderCreateForm(request.POST)
        quantity = int(request.POST.get('quantity', 1))
        if form.is_valid() and quantity > 0 and quantity <= product.stock:
            order = form.save(commit=False)
            order.buyer = request.user
            order.seller = product.seller
            order.total_amount = product.price * quantity
            # GPS récupérés depuis le formulaire :
            order.delivery_lat = request.POST.get('delivery_lat') or None
            order.delivery_lng = request.POST.get('delivery_lng') or None
            order.save()
            OrderItem.objects.create(order=order, product=product, quantity=quantity, price=product.price)
            # Diminuer le stock
            product.stock -= quantity
            product.save()
            # Livraison
            Delivery.objects.create(
                order=order,
                address=order.delivery_address,
                delivery_lat=order.delivery_lat,
                delivery_lng=order.delivery_lng,
                status='pending'
            )
            # NOTIFICATION au vendeur
            notify_user(
                user=order.seller,
                message=f"Nouvelle commande #{order.pk} de la part de {order.buyer.username}.",
                url=f"/orders/{order.pk}/",
                subject="Nouvelle commande reçue",
                email_message=f"Vous avez reçu une nouvelle commande #{order.pk}. Connectez-vous pour la traiter."
            )
            messages.success(request, 'Commande passée avec succès !')
            return redirect('orders:detail', pk=order.pk)
        else:
            messages.error(request, "Quantité invalide ou stock insuffisant.")
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order_create.html', {'form': form, 'product': product})





def order_checkout(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.buyer:
        messages.warning(request, "Seuls les acheteurs peuvent payer cette commande.")
        return redirect('orders:detail', pk=pk)
    product = order.items.first().product  # On suppose un produit par commande, sinon adapte
    if request.method == 'POST':
        form = CheckoutForm(request.POST)
        if form.is_valid():
            # Paiement déjà fait ?
            if hasattr(order, 'payment'):
                messages.info(request, "Le paiement a déjà été enregistré pour cette commande.")
                return redirect('orders:detail', pk=pk)
            # Crée le paiement
            payment = Payment.objects.create(
                order=order,
                user=request.user,
                amount=order.total_amount,
                method=form.cleaned_data['payment_method'],
                status='completed' if form.cleaned_data['payment_method'] in ['cash', 'boutique'] else 'pending',
            )
            if form.cleaned_data['payment_method'] == 'mobile_money':
                payment.transaction_id = f"MM{order.pk}{request.user.pk}"
                payment.save()
            elif form.cleaned_data['payment_method'] == 'credit_card':
                payment.transaction_id = f"CC{order.pk}{request.user.pk}"
                payment.save()
            messages.success(request, "Paiement effectué (ou en attente de validation) !")
            return redirect('orders:detail', pk=pk)
    else:
        form = CheckoutForm(initial={'quantity': order.items.first().quantity})
    return render(request, 'orders/order_checkout.html', {'form': form, 'product': product, 'order': order})






@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('orders:list')
    orders = Order.objects.filter(seller=request.user)
    total_orders = orders.count()
    total_sales = sum([o.total_amount for o in orders])
    total_paid = sum([o.payment.amount for o in orders if hasattr(o, 'payment') and o.payment.status == 'completed'])
    deliveries = Delivery.objects.filter(order__seller=request.user)
    return render(request, 'orders/seller_dashboard.html', {
        'orders': orders,
        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_paid': total_paid,
        'deliveries': deliveries,
    })




import csv
from django.http import HttpResponse
from .models import Order

@login_required
def export_orders_csv(request):
    if not request.user.is_staff and request.user.role != 'seller':
        return redirect('orders:list')
    # Pour un vendeur : seulement ses commandes
    if request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user)
    else:
        orders = Order.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="commandes.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Acheteur', 'Vendeur', 'Montant total', 'Statut', 'Date'])
    for o in orders:
        writer.writerow([o.pk, o.buyer.username, o.seller.username, o.total_amount, o.status, o.created_at])
    return response




from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from .models import Order
from django.contrib.auth.decorators import login_required

@login_required
def export_orders_pdf(request):
    if not request.user.is_staff and request.user.role != 'seller':
        return redirect('orders:list')
    if request.user.role == 'seller':
        orders = Order.objects.filter(seller=request.user)
    else:
        orders = Order.objects.all()
    html_string = render_to_string('orders/orders_pdf.html', {'orders': orders})
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="commandes.pdf"'
    html.write_pdf(response)
    return response




@login_required
def invoice_pdf(request, pk):
    order = get_object_or_404(Order, pk=pk)
    if request.user != order.buyer and request.user != order.seller and not request.user.is_staff:
        return redirect('orders:list')
    html_string = render_to_string('orders/invoice.html', {'order': order})
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="facture_commande_{order.pk}.pdf"'
    html.write_pdf(response)
    return response




@login_required
def order_history(request):
    role = getattr(request.user, 'role', None)
    if role == 'buyer':
        orders = Order.objects.filter(buyer=request.user)
    elif role == 'seller':
        orders = Order.objects.filter(seller=request.user)
    else:
        orders = Order.objects.none()
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    return render(request, 'orders/order_history.html', {'orders': orders})