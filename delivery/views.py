from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Delivery
from accounts.models import DeliveryProfile
from orders.models import Order
from .forms import AssignDeliveryForm, NotationForm
from django.utils import timezone
from django.contrib import messages
import random
import string
import io
import qrcode
from notifications.utils import notify_user
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest
from payments.models import Payment
from django import forms
from django.http import HttpResponse
from django.db.models import Avg

@login_required
def delivery_list(request):
    if request.user.role == 'delivery':
        deliveries = Delivery.objects.filter(delivery_person=request.user)
    elif request.user.role == 'seller':
        deliveries = Delivery.objects.filter(order__seller=request.user)
    else:
        deliveries = Delivery.objects.filter(order__buyer=request.user)
    return render(request, 'delivery/delivery_list.html', {'deliveries': deliveries})

@login_required
def delivery_detail(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if not (
        request.user == delivery.delivery_person or
        request.user == delivery.order.buyer or
        request.user == delivery.order.seller
    ):
        return redirect('delivery:list')
    return render(request, 'delivery/delivery_detail.html', {'delivery': delivery})

@require_POST
def update_position(request, pk):
    # Vérifie que c'est bien le livreur assigné
    delivery = get_object_or_404(Delivery, pk=pk)
    user = request.user
    if not user.is_authenticated or user != delivery.delivery_person:
        return JsonResponse({'error': 'Non autorisé'}, status=403)
    try:
        lat = float(request.POST.get('lat'))
        lng = float(request.POST.get('lng'))
    except (TypeError, ValueError):
        return HttpResponseBadRequest("Coordonnées invalides")
    delivery.current_lat = lat
    delivery.current_lng = lng
    delivery.save(update_fields=['current_lat', 'current_lng'])
    return JsonResponse({'status': 'ok'})



@login_required
@require_POST
def start_delivery(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk, delivery_person=request.user)
    if delivery.status == 'assigned':
        delivery.status = 'in_transit'
        delivery.save()
        messages.success(request, "La livraison est démarrée.")
    return redirect('delivery:detail', pk=pk)


@login_required
def assign_delivery(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    if hasattr(order, 'delivery'):
        messages.warning(request, "Une livraison existe déjà pour cette commande.")
        return redirect('delivery:detail', pk=order.delivery.pk)
    if request.method == 'POST':
        form = AssignDeliveryForm(request.POST)
        if form.is_valid():
            delivery = form.save(commit=False)
            delivery.order = order
            delivery.status = 'assigned'
            delivery.assigned_at = timezone.now()
            delivery.delivery_code = ''.join(random.choices(string.digits, k=6))
            delivery.save()
            # NOTIFICATION au livreur
            if delivery.delivery_person:
                notify_user(
                    user=delivery.delivery_person,
                    message=f"Nouvelle livraison à effectuer pour la commande #{order.pk}.",
                    url=f"/delivery/{delivery.pk}/",
                    subject="Nouvelle livraison à effectuer",
                    email_message=f"Vous avez une livraison à effectuer pour la commande #{order.pk}."
                )
            messages.success(request, "Livreur assigné avec succès.")
            return redirect('delivery:detail', pk=delivery.pk)
    else:
        form = AssignDeliveryForm()
    return render(request, 'delivery/assign_delivery.html', {'form': form, 'order': order})

@login_required
def mark_delivered(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk, delivery_person=request.user)
    if request.method == 'POST':
        code = request.POST.get('delivery_code')
        if code == delivery.delivery_code:
            delivery.status = 'delivered'
            delivery.delivered_at = timezone.now()
            delivery.save()
            order = delivery.order
            order.status = 'delivered'
            order.save()
            notify_user(
                user=delivery.order.buyer,
                message=f"Votre commande #{delivery.order.pk} a été livrée.",
                url=f"/orders/{delivery.order.pk}/",
                subject="Commande livrée",
                email_message=f"Votre commande #{delivery.order.pk} a bien été livrée. Merci pour votre confiance !"
            )
            messages.success(request, "Livraison confirmée !")
            return redirect('delivery:detail', pk=delivery.pk)
        else:
            messages.error(request, "Code de livraison incorrect.")
    return render(request, 'delivery/mark_delivered.html', {'delivery': delivery})

@login_required
def delivery_dashboard(request):
    if request.user.role != 'delivery':
        return redirect('delivery:list')
    deliveries = Delivery.objects.filter(delivery_person=request.user)
    nb_en_attente = deliveries.filter(status='assigned').count()
    nb_livrees = deliveries.filter(status='delivered').count()
    nb_total = deliveries.count()
    return render(request, 'delivery/delivery_dashboard.html', {
        'deliveries': deliveries,
        'nb_en_attente': nb_en_attente,
        'nb_livrees': nb_livrees,
        'nb_total': nb_total,
    })





@login_required
def delivery_qr(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.user != delivery.delivery_person:
        return HttpResponse(status=403)
    scan_url = request.build_absolute_uri(
        f"/delivery/scan/{delivery.qr_token}/"
    )
    img = qrcode.make(scan_url)
    buf = io.BytesIO()
    img.save(buf)
    buf.seek(0)
    return HttpResponse(buf.read(), content_type="image/png")

@login_required
def scan_qr(request, qr_token):
    delivery = get_object_or_404(Delivery, qr_token=qr_token)
    order = delivery.order
    if request.user != order.buyer:
        return HttpResponse("Vous n'êtes pas autorisé à valider cette livraison.", status=403)
    if delivery.status != 'in_transit':
        return render(request, 'delivery/scan_result.html', {'message': "Cette livraison n'est pas en cours ou déjà validée."})
    # Validation de la livraison
    delivery.status = 'delivered'
    delivery.delivered_at = timezone.now()
    delivery.save()
    order.status = 'delivered'
    order.save()
    # Paiement effectif
    try:
        payment = Payment.objects.get(order=order)
        if payment.status != 'completed':
            # Paiement par Mobile Money / Stripe = prélèvement ici
            if payment.method in ['mobile_money', 'credit_card']:
                # Ici, appelle l'API réelle (Stripe/Mobile Money) si besoin
                # Ex : stripe.charge(payment) ou mobile_money_api.charge(payment)
                # Pour l’exemple, on simule l’effet :
                payment.status = 'completed'
                payment.transaction_id = payment.transaction_id or f"TRX{order.pk}{order.buyer.pk}"
                payment.save()
            elif payment.method == 'cash':
                payment.status = 'pending'  # Cash = paiement manuel à la main
                payment.save()
    except Payment.DoesNotExist:
        payment = None
    # Notifications
    notify_user(
        user=order.seller,
        message=f"Commande #{order.pk} livrée et payée.",
        url=f"/orders/{order.pk}/",
        subject="Commande livrée et payée",
        email_message=f"La commande #{order.pk} vient d'être livrée et le paiement validé."
    )
    if delivery.delivery_person:
        notify_user(
            user=delivery.delivery_person,
            message=f"Livraison de la commande #{order.pk} validée et payée.",
            url=f"/delivery/{delivery.pk}/",
            subject="Livraison validée et payée",
        )
    return render(request, 'delivery/scan_result.html', {'message': "Livraison confirmée et paiement effectué !"})




@login_required
def delivery_history(request):
    if request.user.role == 'delivery':
        deliveries = Delivery.objects.filter(delivery_person=request.user)
    elif request.user.role == 'seller':
        deliveries = Delivery.objects.filter(order__seller=request.user)
    else:
        deliveries = Delivery.objects.filter(order__buyer=request.user)
    status = request.GET.get('status')
    if status:
        deliveries = deliveries.filter(status=status)
    return render(request, 'delivery/delivery_history.html', {'deliveries': deliveries})




@login_required
def noter_livreur(request, pk):
    delivery = get_object_or_404(Delivery, pk=pk)
    if request.user != delivery.order.buyer or delivery.status != 'delivered':
        return redirect('delivery:detail', pk=pk)
    if delivery.note:
        return render(request, 'delivery/notation_result.html', {'message': "Vous avez déjà noté ce livreur."})
    if request.method == 'POST':
        form = NotationForm(request.POST, instance=delivery)
        if form.is_valid():
            form.save()
            # Mettre à jour la moyenne sur le profil
            livreur = delivery.delivery_person
            notes = Delivery.objects.filter(delivery_person=livreur, note__isnull=False)
            avg = notes.aggregate(Avg('note'))['note__avg'] or 0
            dp, created = DeliveryProfile.objects.get_or_create(user=livreur)
            dp.rating = avg
            dp.save()
            return render(request, 'delivery/notation_result.html', {'message': "Merci pour votre notation du livreur !"})
    else:
        form = NotationForm()
    return render(request, 'delivery/noter_livreur.html', {'form': form, 'delivery': delivery})