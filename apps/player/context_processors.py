from ..notifications.models import Notifications

def add_notifications_to_context(request):
    username = request.user.username
    notifications = Notifications.objects.filter(destination=username)
    return {
        'notifications': notifications,
        'count':len(notifications),
    }