from django.core.mail import send_mail
from django.conf import settings
from .models import Notification

# Pour Channels
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

def notify_user(user, message, url=None, subject=None, email_message=None):
    # Notif en base
    Notification.objects.create(user=user, message=message, url=url or '')

    # Notif mail si email et sujet fournis
    if subject and user.email:
        send_mail(
            subject=subject,
            message=email_message or message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=True,
        )

    # Notif temps réel via Django Channels
    try:
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"user_{user.id}",
            {
                "type": "send_notification",
                "data": {
                    "message": message,
                    "url": url or "",
                    "subject": subject or "",
                }
            }
        )
    except Exception as e:
        pass  # En prod, loggue l'erreur si besoin