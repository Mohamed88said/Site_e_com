from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def notifications(request):
    notes = request.user.notifications.order_by('-created_at')
    return render(request, 'notifications/notifications_list.html', {'notes': notes})