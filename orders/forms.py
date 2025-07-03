from django import forms
from .models import Order

class OrderCreateForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['delivery_address', 'note']

from django import forms
from orders.models import Order
from payments.models import Payment
from delivery.models import Delivery

class CheckoutForm(forms.Form):
    quantity = forms.IntegerField(min_value=1, initial=1, label="Quantité")
    delivery_method = forms.ChoiceField(
        choices=Delivery.STATUS_CHOICES,
        label="Mode de livraison",
        widget=forms.RadioSelect
    )
    payment_method = forms.ChoiceField(
        choices=Payment.METHOD_CHOICES,
        label="Mode de paiement",
        widget=forms.RadioSelect
    )
    phone_number = forms.CharField(required=False, label="Téléphone Mobile Money")
    delivery_address = forms.CharField(required=False, label="Adresse de livraison")
    note = forms.CharField(widget=forms.Textarea, required=False, label="Note (optionnel)")

    def clean(self):
        cleaned_data = super().clean()
        delivery_method = cleaned_data.get('delivery_method')
        payment_method = cleaned_data.get('payment_method')
        phone_number = cleaned_data.get('phone_number')
        delivery_address = cleaned_data.get('delivery_address')
        if payment_method == 'mobile_money' and not phone_number:
            self.add_error('phone_number', "Le numéro Mobile Money est obligatoire.")
        if delivery_method == 'home' and not delivery_address:
            self.add_error('delivery_address', "L'adresse de livraison est obligatoire.")
        return cleaned_data