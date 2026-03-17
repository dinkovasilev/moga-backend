from django.urls import path
from .views import lobby , notify, sse_stream
from .consumers import NotifyConsumer


urlpatterns = [
    path('socket/<str:target_type>/<str:lobby_name>/', lobby, name='lobby-name'),
    path('stream/', sse_stream, name='event-stream'),
    ]