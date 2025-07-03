from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import User, SellerProfile, DeliveryProfile

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'address', 'role', 'profile_picture', 'password1', 'password2']

class SellerProfileForm(forms.ModelForm):
    class Meta:
        model = SellerProfile
        fields = ['shop_name', 'shop_description', 'shop_logo']

class DeliveryProfileForm(forms.ModelForm):
    class Meta:
        model = DeliveryProfile
        fields = ['vehicle_type', 'available']

class LoginForm(AuthenticationForm):
    pass