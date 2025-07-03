from django.db import models
from accounts.models import User
from orders.models import Order
import uuid

class Delivery(models.Model):
    METHOD_CHOICES = [
        ('home', 'Livraison à domicile'),
        ('boutique', 'Retrait en boutique'),
        ('seller', 'Livraison par le vendeur'),
        ('personal', 'Livreur personnel'),
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('assigned', 'Assignée'),
        ('in_transit', 'En livraison'),
        ('delivered', 'Livrée'),
        ('failed', 'Échec'),
        ('cancelled', 'Annulée'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='delivery')
    method = models.CharField(max_length=20, choices=METHOD_CHOICES, default='home')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    delivery_person = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        limit_choices_to={'role': 'delivery'}, related_name='deliveries'
    )
    assigned_at = models.DateTimeField(null=True, blank=True)
    delivered_at = models.DateTimeField(null=True, blank=True)
    address = models.CharField(max_length=255, blank=True, help_text="Adresse de livraison, si applicable")
    delivery_code = models.CharField(max_length=12, blank=True, help_text="Code secret à remettre lors de la livraison (pour QR code)")
    comment = models.TextField(blank=True, help_text="Informations ou instructions complémentaires")
    delivery_lat = models.FloatField(null=True, blank=True)
    delivery_lng = models.FloatField(null=True, blank=True)
    current_lat = models.FloatField(null=True, blank=True)
    current_lng = models.FloatField(null=True, blank=True)
    qr_token = models.CharField(max_length=64, unique=True, blank=True, null=True)  # Ajout QR

    # AJOUT POUR LA NOTATION DU LIVREUR :
    note = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Note du livreur (1 à 5)")
    commentaire = models.TextField(blank=True, help_text="Commentaire du client sur le livreur")

    def save(self, *args, **kwargs):
        if not self.qr_token:
            self.qr_token = uuid.uuid4().hex
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Livraison pour {self.order} ({self.get_method_display()})"