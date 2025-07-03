from .models import Badge, SellerBadge, Product, Review
from orders.models import OrderItem
from django.utils import timezone
from django.db import models

def check_and_award_badges(user):
    if user.role != 'seller':
        return

    # Badge "Nouveau vendeur"
    badge, _ = Badge.objects.get_or_create(
        name="Nouveau vendeur",
        defaults={"description": "Bienvenue sur la plateforme !", "icon": "🌱"}
    )
    SellerBadge.objects.get_or_create(seller=user, badge=badge)

    # Badge "+100 ventes"
    total_sales = OrderItem.objects.filter(product__seller=user).count()
    badge, _ = Badge.objects.get_or_create(
        name="+100 ventes",
        defaults={"description": "Vous avez dépassé 100 ventes !", "icon": "🔥"}
    )
    if total_sales >= 100:
        SellerBadge.objects.get_or_create(seller=user, badge=badge)

    # Badge "Super vendeur"
    avg_rating = Review.objects.filter(product__seller=user).aggregate(avg=models.Avg('rating'))['avg'] or 0
    badge, _ = Badge.objects.get_or_create(
        name="Super vendeur",
        defaults={"description": "Note moyenne supérieure à 4.7", "icon": "⭐"}
    )
    if avg_rating >= 4.7:
        SellerBadge.objects.get_or_create(seller=user, badge=badge)

    # Badge "Réactif"
    badge, _ = Badge.objects.get_or_create(
        name="Réactif",
        defaults={"description": "Vous répondez vite aux questions des clients", "icon": "⚡"}
    )
    from .models import ProductQuestion
    questions = ProductQuestion.objects.filter(product__seller=user, answer__isnull=False)
    # Si au moins 5 questions ont été répondues en moins de 2h
    fast_answers = [q for q in questions if q.answered_at and (q.answered_at - q.created_at).total_seconds() < 7200]
    if len(fast_answers) >= 5:
        SellerBadge.objects.get_or_create(seller=user, badge=badge)