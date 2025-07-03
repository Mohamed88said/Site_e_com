from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Avg, Count
from django.http import JsonResponse, HttpResponse
from .models import Product, Category, ProductImage, ProductVariant, Review, Wishlist, ProductReport, ProductQuestion
from .forms import ProductForm, ProductImageForm, ProductVariantForm, ReviewForm, WishlistForm, ProductReportForm, ProductQuestionForm, CategoryForm, PromotionForm
from accounts.models import SellerProfile, User
from orders.models import OrderItem
from .models import Category
from notifications.models import Notification
from django.db.models import Sum, F
from .models import Product, Review, ReviewLike, ProductQuestion, QuestionLike
from .forms import ReviewForm, ProductQuestionForm
from django.http import  HttpResponseForbidden
from .models import  SellerBadge
from .badges_utils import check_and_award_badges







# Liste produits avec recherche/filtre/tri
from .forms import ProductFilterForm

from django.db.models import Q

def product_list(request):
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.filter(parent__isnull=True)
    form = ProductFilterForm(request.GET or None)
    if form.is_valid():
        data = form.cleaned_data
        if data['search']:
            products = products.filter(
                Q(name__icontains=data['search']) | Q(description__icontains=data['search'])
            )
        if data['category']:
            products = products.filter(category=data['category'])
        if data['price_min'] is not None:
            products = products.filter(price__gte=data['price_min'])
        if data['price_max'] is not None:
            products = products.filter(price__lte=data['price_max'])
        if data['in_stock']:
            products = products.filter(stock__gt=0)
        if data['promo']:
            # Correction ici : adapte selon ton modèle
            products = products.filter(promotions__isnull=False).distinct()
            # Ou, si tu as un booléen:
            # products = products.filter(has_promo=True)
        if data['with_image']:
            products = products.filter(main_image__isnull=False)
    count = products.count()
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'form': form,
        'count': count,
    })

def product_list_by_category(request, pk):
    cat = get_object_or_404(Category, pk=pk)
    products = cat.products.filter(is_active=True)
    categories = Category.objects.filter(parent__isnull=True)
    return render(request, 'products/product_list.html', {
        'products': products,
        'categories': categories,
        'cat': pk,
        'query': '',
    })

def product_search(request):
    return product_list(request)

# Détail produit
def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, is_active=True)
    reviews = product.reviews.filter(approved=True)
    review_form = None
    already_reviewed = False
    if request.user.is_authenticated and request.user.role == 'buyer':
        already_reviewed = product.reviews.filter(user=request.user).exists()
        if not already_reviewed:
            review_form = ReviewForm()
            if request.method == 'POST' and 'review_submit' in request.POST:
                review_form = ReviewForm(request.POST, request.FILES)
                if review_form.is_valid():
                    review = review_form.save(commit=False)
                    review.user = request.user
                    review.product = product
                    review.save()
                    messages.success(request, "Votre avis a été soumis et sera affiché après validation.")
                    return redirect('products:detail', pk=pk)

    # Questions/réponses
    question_form = None
    if request.user.is_authenticated and request.user.role in ['buyer', 'seller']:
        question_form = ProductQuestionForm()
        if request.method == 'POST' and 'question_submit' in request.POST:
            question_form = ProductQuestionForm(request.POST)
            if question_form.is_valid():
                q = question_form.save(commit=False)
                q.user = request.user
                q.product = product
                q.save()
                messages.success(request, "Votre question a été envoyée au vendeur.")
                return redirect('products:detail', pk=pk)

    # Favoris
    is_favorite = False
    if request.user.is_authenticated:
        is_favorite = product.wishlisted_by.filter(user=request.user).exists()

    # Produits similaires
    similar = Product.objects.filter(category=product.category).exclude(pk=product.pk)[:4]

    # Tri des avis
    sort = request.GET.get('sort', 'recent')
    if sort == 'best':
        reviews = reviews.annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')
    elif sort == 'photo':
        reviews = reviews.exclude(photo='').order_by('-created_at')
    else:
        reviews = reviews.order_by('-created_at')

    return render(request, 'products/product_detail.html', {
        'product': product,
        'reviews': reviews,
        'review_form': review_form,
        'already_reviewed': already_reviewed,
        'question_form': question_form,
        'is_favorite': is_favorite,
        'similar': similar,
        'sort': sort,
    })







# Dashboard vendeur
@login_required
def my_products(request):
    if request.user.role != 'seller':
        return redirect('accounts:dashboard')
    products = Product.objects.filter(seller=request.user)
    return render(request, 'products/my_products.html', {'products': products})



# Création produit avec catégorie libre


@login_required
def product_create(request):
    if request.user.role != 'seller':
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            new_category_name = form.cleaned_data.get('new_category')
            category, created = Category.objects.get_or_create(name=new_category_name)
            product = form.save(commit=False)
            product.seller = request.user
            product.category = category
            product.save()
            # images multiples
            for img in request.FILES.getlist('image'):
                ProductImage.objects.create(product=product, image=img)
            # Notification stock faible
            if product.is_low_stock:
                if not Notification.objects.filter(user=product.seller, message__icontains=product.name, is_read=False).exists():
                    Notification.objects.create(
                        user=product.seller,
                        message=f"Attention : le stock du produit '{product.name}' est bas ({product.stock} restants).",
                        url=f"/products/{product.pk}/"
                    )
            messages.success(request, "Produit créé avec succès.")
            return redirect('products:my_products')
    else:
        form = ProductForm()
    return render(request, 'products/product_form.html', {'form': form})






# Ajout d'une promotion
@login_required
def add_promotion(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            promo.product = product
            promo.save()
            messages.success(request, "Promotion ajoutée.")
            return redirect('products:detail', pk=product.pk)
    else:
        form = PromotionForm()
    return render(request, 'products/promotion_form.html', {'form': form, 'product': product})









# Edition produit
@login_required
def product_edit(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            new_category_name = form.cleaned_data.get('new_category')
            category, created = Category.objects.get_or_create(name=new_category_name)
            product = form.save(commit=False)
            product.category = category
            product.save()
            # Notification stock faible
            if product.is_low_stock:
                if not Notification.objects.filter(user=product.seller, message__icontains=product.name, is_read=False).exists():
                    Notification.objects.create(
                        user=product.seller,
                        message=f"Attention : le stock du produit '{product.name}' est bas ({product.stock} restants).",
                        url=f"/products/{product.pk}/"
                    )
            messages.success(request, "Produit modifié.")
            return redirect('products:my_products')
    else:
        initial = {'new_category': product.category.name if product.category else ''}
        form = ProductForm(instance=product, initial=initial)
    return render(request, 'products/product_form.html', {'form': form, 'product': product})

# Suppression produit
@login_required
def product_delete(request, pk):
    product = get_object_or_404(Product, pk=pk, seller=request.user)
    if request.method == 'POST':
        product.delete()
        messages.success(request, "Produit supprimé.")
        return redirect('products:my_products')
    return render(request, 'products/product_confirm_delete.html', {'product': product})

# Wishlist (favoris)
from django.shortcuts import get_object_or_404
from .models import Wishlist

@login_required
def wishlist(request):
    wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
    if request.method == 'POST' and 'toggle_public' in request.POST:
        wishlist.is_public = not wishlist.is_public
        wishlist.save()
    return render(request, 'products/wishlist.html', {'wishlist': wishlist})

def public_wishlist(request, slug):
    wishlist = get_object_or_404(Wishlist, slug=slug, is_public=True)
    return render(request, 'products/public_wishlist.html', {'wishlist': wishlist})
@login_required
def add_to_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    messages.success(request, "Ajouté à vos favoris.")
    return redirect('products:detail', pk=pk)

@login_required
def remove_from_wishlist(request, pk):
    product = get_object_or_404(Product, pk=pk)
    Wishlist.objects.filter(user=request.user, product=product).delete()
    messages.success(request, "Retiré de vos favoris.")
    return redirect('products:detail', pk=pk)

# Comparateur de produits (à compléter selon besoins)
def compare_products(request):
    # Ex: ?ids=1,2,3
    ids = request.GET.get('ids', '')
    ids = [int(i) for i in ids.split(',') if i.strip().isdigit()]
    products = Product.objects.filter(pk__in=ids)
    return render(request, 'products/compare.html', {'products': products})

# Signalement produit/vendeur
@login_required
def report_product(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductReportForm(request.POST)
        if form.is_valid():
            report = form.save(commit=False)
            report.reported_by = request.user
            report.product = product
            report.save()
            messages.success(request, "Signalement envoyé.")
            return redirect('products:detail', pk=pk)
    else:
        form = ProductReportForm()
    return render(request, 'products/report_form.html', {'form': form, 'product': product})

# Poser une question
@login_required
def ask_question(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ProductQuestionForm(request.POST)
        if form.is_valid():
            q = form.save(commit=False)
            q.product = product
            q.user = request.user
            q.save()
            messages.success(request, "Question envoyée au vendeur.")
            return redirect('products:detail', pk=pk)
    else:
        form = ProductQuestionForm()
    return render(request, 'products/ask_question.html', {'form': form, 'product': product})

# Fiche vendeur publique
def vendor_profile(request, user_id):
    user = get_object_or_404(User, pk=user_id, role='seller')
    profile = get_object_or_404(SellerProfile, user=user)
    products = Product.objects.filter(seller=user, is_active=True)
    return render(request, 'products/vendor_profile.html', {
        'vendor': user,
        'profile': profile,
        'products': products,
    })

# Export catalogue CSV/PDF — à compléter avec libs externes si besoin
def export_csv(request):
    # Exporte tous les produits du vendeur connecté
    if not request.user.is_authenticated or request.user.role != 'seller':
        return redirect('accounts:dashboard')
    import csv
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="catalogue.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Catégorie', 'Prix', 'Stock'])
    for p in Product.objects.filter(seller=request.user):
        writer.writerow([p.name, p.category, p.price, p.stock])
    return response

def export_pdf(request):
    # À faire avec une lib comme ReportLab ou WeasyPrint
    return HttpResponse("Export PDF à implémenter")






@login_required
def seller_dashboard(request):
    if request.user.role != 'seller':
        return redirect('products:list')

    check_and_award_badges(request.user)  # Attribution automatique des badges

    products = Product.objects.filter(seller=request.user)
    total_products = products.count()
    total_stock = products.aggregate(total=Sum('stock'))['total'] or 0
    products_low_stock = products.filter(stock__lte=5)
    promo_products = products.filter(promotions__end__gte=F('promotions__start')).distinct()
    total_promo = promo_products.count()

    # Statistiques de ventes
    order_items = OrderItem.objects.filter(product__seller=request.user)
    total_sales = order_items.aggregate(total=Sum(F('price') * F('quantity')))['total'] or 0
    total_orders = order_items.values('order').distinct().count()
    sales_by_month = (
        order_items
        .annotate(month=F('order__created_at__month'))
        .values('month')
        .annotate(total=Sum(F('price') * F('quantity')))
        .order_by('month')
    )
    top_products = (
        order_items
        .values('product__name')
        .annotate(quantity=Sum('quantity'))
        .order_by('-quantity')[:5]
    )

    months = [str(i) for i in range(1, 13)]
    sales_data = [0] * 12
    for item in sales_by_month:
        idx = int(item['month']) - 1
        sales_data[idx] = float(item['total'])

    top_products_labels = [p['product__name'] for p in top_products]
    top_products_data = [int(p['quantity']) for p in top_products]

    # Badges du vendeur
    badges = SellerBadge.objects.filter(seller=request.user).select_related('badge')

    context = {
        'total_products': total_products,
        'total_stock': total_stock,
        'products_low_stock': products_low_stock,
        'promo_products': promo_products,
        'total_promo': total_promo,
        'total_sales': total_sales,
        'total_orders': total_orders,
        'sales_data': sales_data,
        'months': months,
        'top_products_labels': top_products_labels,
        'top_products_data': top_products_data,
        'badges': badges,
    }
    return render(request, 'products/seller_dashboard.html', context)


@login_required
def like_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if ReviewLike.objects.filter(review=review, user=request.user).exists():
        ReviewLike.objects.filter(review=review, user=request.user).delete()
        liked = False
    else:
        ReviewLike.objects.create(review=review, user=request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': review.likes_count})



@login_required
def like_question(request, pk):
    question = get_object_or_404(ProductQuestion, pk=pk)
    if QuestionLike.objects.filter(question=question, user=request.user).exists():
        QuestionLike.objects.filter(question=question, user=request.user).delete()
        liked = False
    else:
        QuestionLike.objects.create(question=question, user=request.user)
        liked = True
    return JsonResponse({'liked': liked, 'count': question.likes_count()})



@login_required
def mark_best_answer(request, pk):
    question = get_object_or_404(ProductQuestion, pk=pk)
    if request.user != question.product.seller:
        return HttpResponseForbidden()
    # Un seul best_answer par produit
    ProductQuestion.objects.filter(product=question.product, best_answer=True).update(best_answer=False)
    question.best_answer = True
    question.save()
    return redirect('products:detail', pk=question.product.pk)



def all_reviews(request, pk):
    product = get_object_or_404(Product, pk=pk)
    reviews = product.reviews.filter(approved=True)
    sort = request.GET.get('sort', 'recent')
    if sort == 'best':
        reviews = reviews.annotate(num_likes=Count('likes')).order_by('-num_likes', '-created_at')
    elif sort == 'photo':
        reviews = reviews.exclude(photo='').order_by('-created_at')
    else:
        reviews = reviews.order_by('-created_at')
    return render(request, 'products/all_reviews.html', {
        'product': product,
        'reviews': reviews,
        'sort': sort,
    })



import csv
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from .models import Product

@login_required
def export_catalogue_csv(request):
    if request.user.role != 'seller':
        return redirect('accounts:dashboard')
    products = Product.objects.filter(seller=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="catalogue.csv"'
    writer = csv.writer(response)
    writer.writerow(['Nom', 'Catégorie', 'Prix', 'Stock'])
    for p in products:
        writer.writerow([p.name, p.category, p.price, p.stock])
    return response






import csv
import io

from .forms import CatalogueImportForm
from .models import Product, Category
from django.contrib import messages

@login_required
def import_catalogue(request):
    if request.user.role != 'seller':
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = CatalogueImportForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['file']
            # CSV uniquement ici (pour éviter dépendance pandas)
            if file.name.endswith('.csv'):
                decoded = file.read().decode()
                reader = csv.DictReader(io.StringIO(decoded))
                for row in reader:
                    cat, _ = Category.objects.get_or_create(name=row['Catégorie'])
                    Product.objects.create(
                        name=row['Nom'],
                        category=cat,
                        price=row['Prix'],
                        stock=row['Stock'],
                        seller=request.user
                    )
            messages.success(request, "Catalogue importé !")
            return redirect('products:my_products')
    else:
        form = CatalogueImportForm()
    return render(request, 'products/import_catalogue.html', {'form': form})





from .models import ProductBundle
from .forms import ProductBundleForm

@login_required
def create_bundle(request):
    if request.user.role != 'seller':
        return redirect('accounts:dashboard')
    if request.method == 'POST':
        form = ProductBundleForm(request.POST)
        if form.is_valid():
            bundle = form.save(commit=False)
            bundle.seller = request.user
            bundle.save()
            form.save_m2m()
            messages.success(request, "Bundle créé !")
            return redirect('products:my_products')
    else:
        form = ProductBundleForm()
        form.fields['products'].queryset = Product.objects.filter(seller=request.user)
    return render(request, 'products/create_bundle.html', {'form': form})




@login_required
def compare_products(request):
    ids = request.GET.get('ids', '')
    ids = [int(i) for i in ids.split(',') if i.strip().isdigit()]
    products = Product.objects.filter(pk__in=ids)
    return render(request, 'products/compare.html', {'products': products})