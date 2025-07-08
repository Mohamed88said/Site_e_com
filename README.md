# Guinée Makiti

🛍️ **Guinée Makiti** - Plateforme E-commerce Multi-Vendeurs pour la Guinée

Une plateforme e-commerce complète similaire à Amazon, spécialement conçue pour le marché guinéen avec support pour Mobile Money, livraison GPS, et gestion multi-vendeurs.

## 🌟 Fonctionnalités Principales

### 👥 Gestion Multi-Utilisateurs
- **Acheteurs** : Navigation, commandes, avis, wishlist
- **Vendeurs** : Gestion boutique, produits, commandes, analytics
- **Livreurs** : Suivi GPS, validation QR code, historique
- **Administrateurs** : Dashboard complet, modération

### 🛒 E-commerce Avancé
- Catalogue produits avec filtres avancés
- Système de promotions et badges vendeurs
- Comparateur de produits
- Avis clients avec photos
- Questions/réponses produits
- Wishlist publique/privée
- Bundles de produits

### 💳 Paiements Sécurisés
- Mobile Money (Orange Money, MTN)
- Cartes bancaires (Stripe)
- PayPal
- Paiement à la livraison
- QR codes de paiement

### 🚚 Livraison Intelligente
- Géolocalisation GPS
- Suivi en temps réel
- Validation par QR code
- Modes de livraison multiples
- Notation des livreurs

### 📊 Analytics & Reporting
- Dashboard vendeur avec graphiques
- Export CSV/PDF
- Statistiques de ventes
- Gestion des stocks

### 🔔 Notifications
- Notifications temps réel (WebSocket)
- Emails automatiques
- Alertes stock faible

### 🤖 Intelligence Artificielle
- Assistant IA intégré
- Suggestions automatiques
- Recommandations produits

### 🌍 Internationalisation
- Support Français/Anglais
- Devise locale (Franc Guinéen)
- Adaptation culturelle

## Installation rapide

### Prérequis
- Python 3.8+
- Git
- VS Code (recommandé)

### Installation Automatique

```bash
guinee_makiti/
├── accounts/          # Gestion utilisateurs
├── products/          # Catalogue produits
├── orders/            # Gestion commandes
├── payments/          # Système de paiement
├── delivery/          # Livraisons GPS
├── returns/           # Retours/remboursements
├── notifications/     # Notifications temps réel
├── admin_panel/       # Dashboard admin
├── ia/                # Assistant IA
├── core/              # Pages statiques
├── static/            # Fichiers statiques
├── templates/         # Templates HTML
├── media/             # Fichiers uploadés
└── locale/            # Traductions
```

## ⚙️ Configuration

### Variables d'Environnement (.env)

```env
# Django
SECRET_KEY=votre-clé-secrète
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-app

# Paiements
STRIPE_SECRET_KEY=sk_test_...
PAYPAL_CLIENT_ID=...

# Mobile Money Guinée
ORANGE_MONEY_API_KEY=...
MTN_MOMO_API_KEY=...
```

### Base de Données

**Développement** : SQLite (par défaut)
**Production** : PostgreSQL recommandé

```python
# settings.py pour production
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'guinee_makiti',
        'USER': 'votre_user',
        'PASSWORD': 'votre_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

## 🔧 Développement

### Commandes Utiles

```bash
# Créer des migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Collecter les fichiers statiques
python manage.py collectstatic

# Créer des traductions
python manage.py makemessages -l fr
python manage.py compilemessages

# Tests
python manage.py test
```

### VS Code Configuration

Le projet inclut une configuration VS Code optimisée :
- Débogage Django
- Linting Python
- Support templates Django
- Formatage automatique

## 📱 API REST

L'application inclut une API REST pour :
- Intégration mobile
- Webhooks paiement
- Synchronisation données

Endpoints principaux :
- `/api/products/` - Catalogue produits
- `/api/orders/` - Gestion commandes
- `/api/payments/` - Statuts paiements

## 🔒 Sécurité

- Authentification Django robuste
- Protection CSRF
- Validation des données
- Chiffrement des paiements
- Logs de sécurité

## 🌐 Déploiement

### Heroku
```bash
# Installer Heroku CLI
heroku create guinee-makiti
heroku addons:create heroku-postgresql:hobby-dev
heroku addons:create heroku-redis:hobby-dev
git push heroku main
heroku run python manage.py migrate
```

### VPS/Serveur Dédié
```bash
# Avec Docker
docker-compose up -d

# Ou installation manuelle
pip install gunicorn
gunicorn guinee_makiti.wsgi:application
```

## 🤝 Contribution

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/nouvelle-fonctionnalite`)
3. Commit les changements (`git commit -am 'Ajouter nouvelle fonctionnalité'`)
4. Push vers la branche (`git push origin feature/nouvelle-fonctionnalite`)
5. Créer une Pull Request

## 📄 Licence

Ce projet est sous licence MIT. Voir le fichier `LICENSE` pour plus de détails.

## 🆘 Support

- **Documentation** : Voir le dossier `/docs`
- **Issues** : Utiliser GitHub Issues
- **Email** : support@guinee-makiti.com

## 🙏 Remerciements

- Communauté Django
- Développeurs guinéens
- Contributeurs open source

---

**Guinée Makiti** - Révolutionner le e-commerce en Guinée 🇬🇳
### Installation Manuelle

```bash
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement (Windows)
venv\Scripts\activate
# Ou sur Linux/Mac
# source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configurer l'environnement
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac

# Configurer la base de données
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
## 🚀 Démarrage Rapide

1. **Accéder à l'application** : http://127.0.0.1:8000
2. **Panel admin** : http://127.0.0.1:8000/admin
3. **Créer des comptes de test** :
   - Vendeur : pour gérer une boutique
   - Acheteur : pour passer des commandes
   - Livreur : pour effectuer les livraisons

## 📁 Structure du Projet
