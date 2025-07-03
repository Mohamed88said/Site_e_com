from django import forms
from .models import Product, ProductImage, ProductVariant, Category, Review, Wishlist, ProductReport, ProductQuestion, Promotion, ProductBundle

class ProductForm(forms.ModelForm):
    new_category = forms.CharField(
        required=False,
        label="Nouvelle catégorie",
        help_text="Saisir une nouvelle catégorie si elle n'existe pas dans la liste."
    )

    class Meta:
        model = Product
        fields = [
            'new_category', 'name', 'description', 'price', 'old_price', 'stock',
            'main_image', 'is_active', 'is_featured', 'has_variants'
        ]

class ProductImageForm(forms.ModelForm):
    class Meta:
        model = ProductImage
        fields = ['image']

class ProductVariantForm(forms.ModelForm):
    class Meta:
        model = ProductVariant
        fields = ['name', 'price', 'stock']

class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'parent']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment', 'photo']
        widgets = {
            'rating': forms.NumberInput(attrs={'min': 1, 'max': 5, 'step': 1}),
            'comment': forms.Textarea(attrs={'rows': 3}),
        }

class ProductQuestionForm(forms.ModelForm):
    class Meta:
        model = ProductQuestion
        fields = ['question']
        widgets = {
            'question': forms.Textarea(attrs={'rows': 2}),
        }

class WishlistForm(forms.ModelForm):
    class Meta:
        model = Wishlist
        fields = []

class ProductReportForm(forms.ModelForm):
    class Meta:
        model = ProductReport
        fields = ['report_type', 'reason']


class PromotionForm(forms.ModelForm):
    class Meta:
        model = Promotion
        fields = ['discount_percent', 'start', 'end']
        widgets = {
            'start': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }


from django import forms

class CatalogueImportForm(forms.Form):
    file = forms.FileField(label="Fichier CSV ou Excel")



class ProductBundleForm(forms.ModelForm):
    class Meta:
        model = ProductBundle
        fields = ['name', 'description', 'products', 'price']
        widgets = {
            'products': forms.CheckboxSelectMultiple(),
        }






class ProductFilterForm(forms.Form):
    search = forms.CharField(label="Nom ou description", required=False)
    category = forms.ModelChoiceField(label="Catégorie", queryset=Category.objects.all(), required=False)
    price_min = forms.DecimalField(label="Prix min", required=False, min_value=0, decimal_places=0)
    price_max = forms.DecimalField(label="Prix max", required=False, min_value=0, decimal_places=0)
    in_stock = forms.BooleanField(label="En stock uniquement", required=False)
    promo = forms.BooleanField(label="En promotion", required=False)
    with_image = forms.BooleanField(label="Avec image", required=False)