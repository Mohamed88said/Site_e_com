from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import ReturnRequest
from orders.models import Order
from .forms import ReturnRequestForm
from django.utils import timezone
from django.contrib import messages
from notifications.utils import notify_user

@login_required
def returns_list(request):
    if request.user.role == 'buyer':
        returns = ReturnRequest.objects.filter(user=request.user)
    elif request.user.role == 'seller':
        returns = ReturnRequest.objects.filter(order__seller=request.user)
    else:
        returns = ReturnRequest.objects.all()
    return render(request, 'returns/returns_list.html', {'returns': returns})

@login_required
def return_detail(request, pk):
    return_request = get_object_or_404(ReturnRequest, pk=pk)
    if (request.user != return_request.user and request.user != return_request.order.seller):
        return redirect('returns:list')
    return render(request, 'returns/return_detail.html', {'return_request': return_request})

@login_required
def return_create(request, order_id):
    order = get_object_or_404(Order, pk=order_id, buyer=request.user)
    if hasattr(order, 'return_request'):
        messages.warning(request, "Une demande de retour existe déjà pour cette commande.")
        return redirect('returns:detail', pk=order.return_request.pk)
    if request.method == 'POST':
        form = ReturnRequestForm(request.POST)
        if form.is_valid():
            return_request = form.save(commit=False)
            return_request.order = order
            return_request.user = request.user
            return_request.save()
            # Notification vendeur
            notify_user(
                user=order.seller,
                message=f"Nouvelle demande de retour pour la commande #{order.pk}",
                url=f"/returns/{return_request.pk}/",
                subject="Nouvelle demande de retour",
                email_message=f"Vous avez reçu une nouvelle demande de retour pour la commande #{order.pk}."
            )
            messages.success(request, "Demande de retour envoyée avec succès.")
            return redirect('returns:detail', pk=return_request.pk)
    else:
        form = ReturnRequestForm()
    return render(request, 'returns/return_create.html', {'form': form, 'order': order})

@login_required
def return_process(request, pk):
    return_request = get_object_or_404(ReturnRequest, pk=pk)
    if request.user != return_request.order.seller:
        return redirect('returns:list')
    if request.method == 'POST':
        action = request.POST.get('action')
        message = request.POST.get('response_message', '')
        if action == 'accept':
            return_request.status = 'accepted'
        elif action == 'reject':
            return_request.status = 'rejected'
        return_request.response_message = message
        return_request.processed_at = timezone.now()
        return_request.save()
        # Notification acheteur
        notify_user(
            user=return_request.user,
            message=f"Votre demande de retour pour la commande #{return_request.order.pk} a été {return_request.get_status_display().lower()}.",
            url=f"/returns/{return_request.pk}/",
            subject="Mise à jour de votre retour",
            email_message=f"Votre demande de retour pour la commande #{return_request.order.pk} a été traitée : {return_request.get_status_display()}. Message vendeur : {return_request.response_message}"
        )
        messages.success(request, f"Retour {return_request.status}.")
        return redirect('returns:detail', pk=return_request.pk)
    return render(request, 'returns/return_process.html', {'return_request': return_request})




import csv
from django.http import HttpResponse

@login_required
def export_returns_csv(request):
    if not request.user.is_staff and request.user.role not in ['seller', 'buyer']:
        return redirect('returns:list')
    # Filtrage selon le rôle
    if request.user.role == 'seller':
        returns = ReturnRequest.objects.filter(order__seller=request.user)
    elif request.user.role == 'buyer':
        returns = ReturnRequest.objects.filter(user=request.user)
    else:
        returns = ReturnRequest.objects.all()
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="retours.csv"'
    writer = csv.writer(response)
    writer.writerow(['ID', 'Commande', 'Client', 'Statut', 'Motif', 'Réponse', 'Date demande', 'Date traitement'])
    for r in returns:
        writer.writerow([
            r.pk, r.order.pk, r.user.username, r.get_status_display(), r.reason, r.response_message,
            r.created_at, r.processed_at or ''
        ])
    return response





from django.template.loader import render_to_string
from weasyprint import HTML
from django.http import HttpResponse
from .models import ReturnRequest
from django.contrib.auth.decorators import login_required

@login_required
def export_returns_pdf(request):
    if not request.user.is_staff and request.user.role not in ['seller', 'buyer']:
        return redirect('returns:list')
    if request.user.role == 'seller':
        returns = ReturnRequest.objects.filter(order__seller=request.user)
    elif request.user.role == 'buyer':
        returns = ReturnRequest.objects.filter(user=request.user)
    else:
        returns = ReturnRequest.objects.all()
    html_string = render_to_string('returns/returns_pdf.html', {'returns': returns})
    html = HTML(string=html_string)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="retours.pdf"'
    html.write_pdf(response)
    return response