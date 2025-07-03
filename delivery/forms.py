from django import forms
from .models import Delivery

class AssignDeliveryForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['delivery_person']


class NotationForm(forms.ModelForm):
    class Meta:
        model = Delivery
        fields = ['note', 'commentaire']
        widgets = {
            'note': forms.NumberInput(attrs={'min': 1, 'max': 5}),
            'commentaire': forms.Textarea(attrs={'rows': 2})
        }