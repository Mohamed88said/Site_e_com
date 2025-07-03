import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'remplace_cette_valeur_par_une_cle_secrete_django'

DEBUG = True  # Passe à False en production

ALLOWED_HOSTS = ['*']  # À restreindre en production

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # Apps du projet
    'accounts',
    'products',
    'orders',
    'delivery',
    'payments',
    'returns',
    'admin_panel',
    'ia',
    'core',
    'rest_framework',  # Pour l’API/notifications si besoin
    'notifications',
    'channels',        # <--- Ajoute Channels ici
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'products.middleware.ProductHistoryMiddleware',
]

ROOT_URLCONF = 'guinee_makiti.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'core.context_processors.notifications_count',
            ],
        },
    },
]

WSGI_APPLICATION = 'guinee_makiti.wsgi.application'
ASGI_APPLICATION = 'guinee_makiti.asgi.application'  # <--- Ajoute cette ligne pour Channels

# Channels config (pour développement, backend mémoire)
CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels.layers.InMemoryChannelLayer',  # Pour dev uniquement
    },
}
# Pour la prod tu utiliseras Redis :
# 'BACKEND': 'channels_redis.core.RedisChannelLayer',
# 'CONFIG': {"hosts": [("localhost", 6379)]},

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

AUTH_USER_MODEL = 'accounts.User'

LANGUAGE_CODE = 'fr'
LANGUAGES = [
    ('fr', 'Français'),
    ('en', 'English'),
]
TIME_ZONE = 'Africa/Conakry'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static']
STATIC_ROOT = BASE_DIR / 'staticfiles'

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/accounts/dashboard/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

# Stripe/Paypal/Mobile Money config à compléter dans .env
STRIPE_PUBLIC_KEY = os.environ.get('STRIPE_PUBLIC_KEY', '')
STRIPE_SECRET_KEY = os.environ.get('STRIPE_SECRET_KEY', '')
PAYPAL_CLIENT_ID = os.environ.get('PAYPAL_CLIENT_ID', '')
PAYPAL_CLIENT_SECRET = os.environ.get('PAYPAL_CLIENT_SECRET', '')

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = '<mohamedsaiddiallo88@gmail.com>'
EMAIL_HOST_PASSWORD = 'TON_MOT_DE_PASSE_GMAIL'
DEFAULT_FROM_EMAIL = '<mohamedsaiddiallo88@gmail.com>'

# Sécurité en prod :
# CSRF_COOKIE_SECURE = True
# SESSION_COOKIE_SECURE = True