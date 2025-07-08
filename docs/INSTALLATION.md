# Guide d'Installation - Guinée Makiti

## Prérequis

### Système d'exploitation
- Windows 10/11 (recommandé pour ce guide)
- macOS 10.15+
- Ubuntu 18.04+

### Logiciels requis
- **Python 3.8+** : [Télécharger Python](https://www.python.org/downloads/)
- **Git** : [Télécharger Git](https://git-scm.com/downloads)
- **VS Code** : [Télécharger VS Code](https://code.visualstudio.com/)

### Extensions VS Code recommandées
- Python
- Django
- GitLens
- Prettier
- Auto Rename Tag

## Installation sur Windows

### 1. Préparation de l'environnement

```cmd
# Vérifier Python
python --version

# Vérifier Git
git --version

# Vérifier pip
pip --version
```

### 2. Cloner le projet

```cmd
# Cloner depuis GitHub
git clone https://github.com/votre-username/guinee-makiti.git
cd guinee-makiti

# Ou créer un nouveau projet
mkdir guinee-makiti
cd guinee-makiti
```

### 3. Installation automatique

```cmd
# Lancer le script d'installation
python setup_project.py
```

Le script va automatiquement :
- Créer l'environnement virtuel
- Installer les dépendances
- Configurer la base de données
- Créer les fichiers de configuration VS Code

### 4. Installation manuelle (alternative)

```cmd
# Créer l'environnement virtuel
python -m venv venv

# Activer l'environnement virtuel
venv\Scripts\activate

# Mettre à jour pip
python -m pip install --upgrade pip

# Installer les dépendances
pip install -r requirements.txt

# Copier le fichier d'environnement
copy .env.example .env

# Créer les migrations
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Créer un superutilisateur
python manage.py createsuperuser

# Collecter les fichiers statiques
python manage.py collectstatic --noinput
```

### 5. Configuration

Éditer le fichier `.env` :

```env
SECRET_KEY=votre-clé-secrète-très-longue-et-complexe
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Email (optionnel pour le développement)
EMAIL_HOST_USER=votre-email@gmail.com
EMAIL_HOST_PASSWORD=votre-mot-de-passe-application

# Paiements (optionnel pour le développement)
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
```

### 6. Lancement

```cmd
# Activer l'environnement virtuel
venv\Scripts\activate

# Lancer le serveur de développement
python manage.py runserver

# Ou avec une IP spécifique
python manage.py runserver 0.0.0.0:8000
```

Accéder à l'application :
- **Site principal** : http://127.0.0.1:8000
- **Administration** : http://127.0.0.1:8000/admin

## Installation sur macOS/Linux

### 1. Préparation

```bash
# Installer Python (si nécessaire)
# macOS avec Homebrew
brew install python

# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Vérifier l'installation
python3 --version
pip3 --version
```

### 2. Installation du projet

```bash
# Cloner le projet
git clone https://github.com/votre-username/guinee-makiti.git
cd guinee-makiti

# Créer l'environnement virtuel
python3 -m venv venv

# Activer l'environnement virtuel
source venv/bin/activate

# Installer les dépendances
pip install -r requirements.txt

# Configuration
cp .env.example .env

# Base de données
python manage.py migrate

# Superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

## Configuration VS Code

### 1. Ouvrir le projet

```cmd
# Ouvrir VS Code dans le dossier du projet
code .
```

### 2. Sélectionner l'interpréteur Python

1. `Ctrl+Shift+P` (Windows) ou `Cmd+Shift+P` (macOS)
2. Taper "Python: Select Interpreter"
3. Choisir `./venv/Scripts/python.exe` (Windows) ou `./venv/bin/python` (macOS/Linux)

### 3. Configuration du débogage

Le fichier `.vscode/launch.json` est automatiquement créé avec :

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Django",
            "type": "python",
            "request": "launch",
            "program": "${workspaceFolder}/manage.py",
            "args": ["runserver"],
            "django": true,
            "justMyCode": true
        }
    ]
}
```

### 4. Lancement depuis VS Code

- Appuyer sur `F5` pour lancer en mode débogage
- Ou utiliser le terminal intégré : `Ctrl+`` `

## Données de test

### Créer des utilisateurs de test

```python
# Dans le shell Django
python manage.py shell

# Créer des utilisateurs
from accounts.models import User
from accounts.models import SellerProfile, DeliveryProfile

# Vendeur
seller = User.objects.create_user(
    username='vendeur_test',
    email='vendeur@test.com',
    password='motdepasse123',
    role='seller'
)
SellerProfile.objects.create(
    user=seller,
    shop_name='Boutique Test',
    shop_description='Une boutique de test'
)

# Acheteur
buyer = User.objects.create_user(
    username='acheteur_test',
    email='acheteur@test.com',
    password='motdepasse123',
    role='buyer'
)

# Livreur
delivery = User.objects.create_user(
    username='livreur_test',
    email='livreur@test.com',
    password='motdepasse123',
    role='delivery'
)
DeliveryProfile.objects.create(
    user=delivery,
    vehicle_type='Moto'
)
```

### Créer des produits de test

```python
from products.models import Category, Product

# Catégorie
cat = Category.objects.create(
    name='Électronique',
    description='Produits électroniques'
)

# Produit
Product.objects.create(
    name='Smartphone Test',
    description='Un smartphone de test',
    price=500000,  # 500,000 GNF
    stock=10,
    category=cat,
    seller=seller,
    is_active=True
)
```

## Dépannage

### Problèmes courants

#### 1. Erreur "python n'est pas reconnu"
```cmd
# Ajouter Python au PATH Windows
# Ou utiliser py au lieu de python
py --version
py -m venv venv
```

#### 2. Erreur de permissions (macOS/Linux)
```bash
# Utiliser sudo si nécessaire
sudo pip3 install -r requirements.txt

# Ou changer les permissions
chmod +x manage.py
```

#### 3. Erreur de base de données
```cmd
# Supprimer la base de données et recommencer
del db.sqlite3
python manage.py migrate
```

#### 4. Erreur de modules manquants
```cmd
# Réinstaller les dépendances
pip install -r requirements.txt --force-reinstall
```

### Logs et débogage

```python
# Dans settings.py pour plus de logs
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
```

## Prochaines étapes

1. **Personnalisation** : Modifier les templates et styles
2. **Configuration email** : Configurer SMTP pour les notifications
3. **Paiements** : Configurer Stripe et Mobile Money
4. **Déploiement** : Préparer pour la production

Voir les autres guides dans le dossier `docs/` pour plus de détails.