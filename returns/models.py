from django.db import models
from orders.models import Order
from accounts.models import User

class ReturnRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'En attente'),
        ('accepted', 'Accepté'),
        ('rejected', 'Refusé'),
        ('refunded', 'Remboursé'),
    ]
    order = models.OneToOneField(Order, on_delete=models.CASCADE, related_name='return_request')
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Celui qui fait la demande (acheteur)
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    response_message = models.TextField(blank=True)

    def __str__(self):
        return f"Retour #{self.pk} - Commande #{self.order.pk} ({self.status})"