from django.urls import path
from .views import (
    TaskCreateMessage,
    ItemCreateMessage,
    item_save_message,
    message_up_vote,
    message_down_vote,
)

urlpatterns = [
        path('task/create-message/<str:task_id>',
            TaskCreateMessage.as_view(), 
            name='task-message'),
        path('item/create-message/<str:item_id>',
            ItemCreateMessage.as_view(),
            name='item-message'), 
        path('item/send-message/',
            item_save_message,name='item-save-message'),    
        path('message/upvote/<str:message_id>/<str:task_id>',
            message_up_vote,name='message-upvote'),
        path('message/downvote/<str:message_id>/<str:task_id>',
            message_down_vote,name='message-downvote'),    
]