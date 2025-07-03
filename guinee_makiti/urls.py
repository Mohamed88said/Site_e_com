from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('products/', include('products.urls', namespace='products')),
    path('orders/', include('orders.urls', namespace='orders')),
    path('delivery/', include('delivery.urls', namespace='delivery')),
    path('payments/', include('payments.urls', namespace='payments')),
    path('returns/', include('returns.urls', namespace='returns')),
    path('admin-panel/', include('admin_panel.urls', namespace='admin_panel')),
    path('ia/', include('ia.urls', namespace='ia')),
    path('', include('core.urls', namespace='core')),  # Accueil, statique, etc.
    path('notifications/', include('notifications.urls', namespace='notifications')),
]

# Internationalisation (multi-langues)
urlpatterns += i18n_patterns(
    # On peut y ajouter des patterns traductibles si besoin
)

# Pour gérer les fichiers médias et statiques en dev
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)