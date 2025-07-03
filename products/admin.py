from django.contrib import admin
from .models import Category, Product, ProductImage, ProductVariant, Review, Wishlist, ProductReport, ProductQuestion

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'seller', 'price', 'stock', 'is_active', 'is_featured')
    list_filter = ('category', 'is_active', 'is_featured')
    search_fields = ('name', 'description')
    inlines = [ProductImageInline, ProductVariantInline]

class ReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'approved', 'created_at')
    list_filter = ('approved', 'created_at')
    search_fields = ('product__name', 'user__username', 'comment')
    actions = ['approve_reviews']

    def approve_reviews(self, request, queryset):
        queryset.update(approved=True)

admin.site.register(Category)
admin.site.register(Product, ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(ProductVariant)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Wishlist)
admin.site.register(ProductReport)
admin.site.register(ProductQuestion)