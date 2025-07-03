from django.db import models
from accounts.models import User

class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.message[:30]}"