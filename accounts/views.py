from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, SellerProfileForm, DeliveryProfileForm, LoginForm
from .models import SellerProfile, DeliveryProfile

def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            role = form.cleaned_data.get('role')
            if role == 'seller':
                SellerProfile.objects.create(user=user)
            elif role == 'delivery':
                DeliveryProfile.objects.create(user=user)
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'accounts/register.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('accounts:dashboard')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})

def user_logout(request):
    logout(request)
    return redirect('accounts:login')

@login_required
def dashboard(request):
    user = request.user
    context = {'user': user}
    if user.role == 'seller':
        context['profile'] = SellerProfile.objects.get(user=user)
    elif user.role == 'delivery':
        context['profile'] = DeliveryProfile.objects.get(user=user)
    return render(request, 'accounts/dashboard.html', context)