from django.urls import path
from .views import (
    ItemDetail, 
    ItemCreate, 
    ItemUpdate,
    ItemDelete,
    ItemDelivery,
    ItemTake,
    ItemCancel,
)

urlpatterns = [
    path('item/details/<str:item_id>/', 
                ItemDetail.as_view(),
                name='item'),
    path('item/create/', 
                ItemCreate.as_view(),
                name='item-create'),
    path('item/update/<str:pk>/', 
                ItemUpdate.as_view(),
                name='item-update'),
    path('item/delete/<str:pk>/', 
                ItemDelete.as_view(),
                name='item-delete'),
    path('item/delivery/<str:item_id>/',
                ItemDelivery.as_view(),
                name='item-deliver'),   
    path('item/take/<str:item_id>/',
                ItemTake.as_view(),
                name='item-take'), 
    path('item/cancel/<str:item_id>/',
                ItemCancel.as_view(),
                name='item-cancel')
]
