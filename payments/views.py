from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from orders.models import Order
from .models import Payment
from .forms import PaymentForm
from django.contrib import messages
import qrcode
from django.core.files import File
from io import BytesIO
from notifications.utils import notify_user

@login_required
def payment_list(request):
    if request.user.role == 'buyer':
        payments = Payment.objects.filter(user=request.user)
    elif request.user.role == 'seller':
        payments = Payment.objects.filter(order__seller=request.user)
    else:
        payments = Payment.objects.all()
    return render(request, 'payments/payment_list.html', {'payments': payments})

@login_required
def payment_detail(request, pk):
    payment = get_object_or_404(Payment, pk=pk)
    if (request.user != payment.user and request.user != payment.order.seller):
        return redirect('payments:list')
    return render(request, 'payments/payment_detail.html', {'payment': payment})

@login_required
def payment_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if hasattr(order, 'payment'):
        messages.warning(request, 'Le paiement a déjà été effectué pour cette commande.')
        return redirect('payments:detail', pk=order.payment.pk)
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.order = order
            payment.user = request.user
            payment.amount = order.total_amount
            # Simulation du paiement
            if payment.method == 'mobile_money':
                payment.status = 'pending'  # Paiement en attente de confirmation
            else:
                payment.status = 'completed'
            payment.transaction_id = f"TXN{order.pk}{payment.user.pk}"
            payment.save()
            # Génération QR code SI Mobile Money
            if payment.method == 'mobile_money':
                generate_payment_qr(payment)
            # NOTIFICATIONS
            # Notifie le vendeur
            notify_user(
                user=payment.order.seller,
                message=f"Paiement reçu pour la commande #{payment.order.pk}.",
                url=f"/orders/{payment.order.pk}/",
                subject="Paiement reçu",
                email_message=f"Votre commande #{payment.order.pk} a été payée."
            )
            # Notifie l'acheteur
            notify_user(
                user=payment.user,
                message=f"Votre paiement pour la commande #{payment.order.pk} a bien été enregistré.",
                url=f"/payments/{payment.pk}/",
                subject="Paiement enregistré",
                email_message=f"Votre paiement pour la commande #{payment.order.pk} est pris en compte."
            )
            messages.success(request, "Paiement enregistré avec succès !")
            return redirect('payments:detail', pk=payment.pk)
    else:
        form = PaymentForm()
    return render(request, 'payments/payment_create.html', {'form': form, 'order': order})

def generate_payment_qr(payment):
    # Personnalise ce qui sera encodé dans le QR (ici : ID paiement, montant, méthode)
    data = f"PAYMENT|order={payment.order.pk}|amount={payment.amount}|method={payment.method}"
    qr = qrcode.make(data)
    buffer = BytesIO()
    qr.save(buffer, format="PNG")
    filename = f"payment_qr_{payment.pk}.png"
    payment.qr_code.save(filename, File(buffer), save=True)






import csv
from django.http import HttpResponse

@login_required
def export_payments_csv(request):
    if not request.user.is_staff and request.user.role not in ['seller', 'buyer']:
        return redirect('payments:list')
    if request.user.role == 'seller':
        payments = Payment.objects.filter(order__seller=request.user)
    elif request.user.role == 'buyer':
        payments = Payment.objects.filter(user=request.user)
    else:
        payments = Payment.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="paiements.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Commande', 'Utilisateur', 'Montant', 'Méthode', 'Statut', 'Date'])
    for p in payments:
        writer.writerow([
            p.pk, p.order.pk, p.user.username, p.amount, p.method, p.status, p.created_at
        ])
    return response



from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from .models import Payment
from django.contrib.auth.decorators import login_required

@login_required
def export_payments_pdf(request):
    if not request.user.is_staff and request.user.role not in ['seller', 'buyer']:
        return redirect('payments:list')
    if request.user.role == 'seller':
        payments = Payment.objects.filter(order__seller=request.user)
    elif request.user.role == 'buyer':
        payments = Payment.objects.filter(user=request.user)
    else:
        payments = Payment.objects.all()
    html_string = render_to_string('payments/payments_pdf.html', {'payments': payments})
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="paiements.pdf"'
    html.write_pdf(response)
    return response