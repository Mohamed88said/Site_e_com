from django.db import models
from orders.models import Order
from accounts.models import User

class Payment(models.Model):
    METHOD_CHOICES = [
        ('mobile_money', 'Mobile Money'),
        ('credit_card', 'Carte bancaire'),
        ('paypal', 'PayPal'),
        ('cash', 'Espèces'),
        # Ajoute d'autres méthodes si besoin
    ]
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('completed', 'Terminé'),
        ('failed', 'Échoué'),
        ('refunded', 'Remboursé'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='payment')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    method = models.CharField(max_length=20, choices=METHOD_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(auto_now_add=True)
    qr_code = models.ImageField(upload_to='payments/qrcodes/', blank=True, null=True)  # Ajout

    def __str__(self):
        return f"{self.order} - {self.method} - {self.status}"