from django.urls import re_path, path

from .consumers import (
    ChatConsumer, 
    NotifyConsumer,
    )

websocket_urlpatterns = [
    
    re_path(r'ws/notification-server/(?P<username>\w+)/$',NotifyConsumer.as_asgi()),
    re_path(r'ws/chat-server/(?P<lobby_name>\w+)/$', ChatConsumer.as_asgi()),
]

