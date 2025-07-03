from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = (
        ('buyer', 'Acheteur'),
        ('seller', 'Vendeur'),
        ('delivery', 'Livreur'),
        ('admin', 'Admin'),
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='buyer')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_verified = models.BooleanField(default=False)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)

class SellerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    shop_name = models.CharField(max_length=100)
    shop_description = models.TextField(blank=True)
    shop_logo = models.ImageField(upload_to='shops/', blank=True, null=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.shop_name

class DeliveryProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vehicle_type = models.CharField(max_length=50, blank=True)
    available = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.user.username} - {self.vehicle_type}"