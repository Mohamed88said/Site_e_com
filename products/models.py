from django.db import models
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, SellerProfile

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='subcategories')

    class Meta:
        verbose_name_plural = "Catégories"

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'seller'}, related_name='products')
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=12, decimal_places=2)
    old_price = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    stock = models.PositiveIntegerField(default=0)
    main_image = models.ImageField(upload_to='products/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    has_variants = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    @property
    def promo(self):
        now = timezone.now()
        return self.promotions.filter(start__lte=now, end__gte=now).first()

    @property
    def promo_price(self):
        promo = self.promo
        if promo:
            return round(self.price * (1 - promo.discount_percent / 100), 2)
        return self.price

    @property
    def is_new(self):
        return (timezone.now() - self.created_at) <= timedelta(days=7)

    @property
    def is_low_stock(self):
        return self.stock <= 5  # Seuil configurable

    @property
    def has_promo(self):
        return bool(self.promo)

class Promotion(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='promotions')
    discount_percent = models.DecimalField(max_digits=5, decimal_places=2)
    start = models.DateTimeField()
    end = models.DateTimeField()

    def is_active(self):
        now = timezone.now()
        return self.start <= now <= self.end

    def __str__(self):
        return f"{self.discount_percent}% du {self.start} au {self.end}"

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=50)
    price = models.DecimalField(max_digits=12, decimal_places=2)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.product.name} - {self.name}"

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/gallery/')


class Review(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(default=5)
    comment = models.TextField(blank=True)
    photo = models.ImageField(upload_to='reviews/photos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=False)

    class Meta:
        unique_together = ('product', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} - {self.product.name} ({self.rating})"

    @property
    def likes_count(self):
        return self.likes.count()

class ReviewLike(models.Model):
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('review', 'user')

class ProductQuestion(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    best_answer = models.BooleanField(default=False)  # Ajout

    def likes_count(self):
        return self.likes.count()


import uuid

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlists')
    products = models.ManyToManyField(Product, related_name='wishlisted_by')
    is_public = models.BooleanField(default=False)
    slug = models.SlugField(unique=True, default=uuid.uuid4)

    def __str__(self):
        return f"Wishlist de {self.user.username}"
    




class ProductReport(models.Model):
    REPORT_TYPE = (('product', 'Produit'), ('seller', 'Vendeur'))
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    seller = models.ForeignKey(SellerProfile, on_delete=models.CASCADE, null=True, blank=True)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPE)
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_resolved = models.BooleanField(default=False)



class ProductQuestion(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, related_name='questions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    question = models.TextField()
    answer = models.TextField(blank=True)
    answered_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='answers')
    created_at = models.DateTimeField(auto_now_add=True)
    answered_at = models.DateTimeField(null=True, blank=True)
    is_public = models.BooleanField(default=True)
    best_answer = models.BooleanField(default=False)  # Uniquement ici

    def likes_count(self):
        return self.likes.count()

class QuestionLike(models.Model):
    question = models.ForeignKey(ProductQuestion, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('question', 'user')


from django.utils import timezone

class Badge(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    icon = models.CharField(max_length=100, blank=True, help_text="Nom Bootstrap icon ou emoji")
    def __str__(self):
        return self.name

class SellerBadge(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    date_awarded = models.DateTimeField(auto_now_add=True)
    class Meta:
        unique_together = ('seller', 'badge')

    def __str__(self):
        return f"{self.seller.username} - {self.badge.name}"
    

from django.conf import settings

class ProductBundle(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    products = models.ManyToManyField('Product', related_name='bundles')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    seller = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def __str__(self):
        return self.name