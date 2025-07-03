# Guinée Makiti

Plateforme e-commerce multi-vendeurs, multi-livreurs, avec paiement sécurisé, gestion livraison QR code, retours et IA.

## Installation rapide

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver