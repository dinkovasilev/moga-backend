from django.urls import path, include
from .views import *

urlpatterns = [
    path('index/',index,name='index'),
    path('json-test/',json_test_view,name='json-test'),
    path('',include('apps.catalogs.urls')),
    path('',include('apps.filters.urls')),
    path('',include('apps.player.urls')),
    path('',include('apps.task.urls')),
    path('',include('apps.message.urls')),
    path('',include('apps.item.urls')),
    path('',include('apps.notifications.urls')),
    path('',include('apps.mobile.urls')),
]

"""
    
    
    
    
    
    
"""
