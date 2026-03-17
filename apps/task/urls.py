from django.urls import path
from .views import (
    home, 
    TaskDetail, 
    TaskCreate, 
    TaskUpdate,
    TaskTakeOrWait,
    TaskActions,
    take_task,
    finish_task,
    abort_task,
    cancel_task,
    remove_task,
    add_listener,
    remove_listener,
    archive_task
)

urlpatterns = [
        path('', home, name='home'),
        path('task/details/<str:task_id>/', TaskDetail.as_view(), name='task'),
        path('task/actions/<str:task_id>',TaskActions.as_view(),name='task-actions'),        
        path('task/create/', TaskCreate.as_view(), name='task-create'),    
        path('task/update/<str:pk>/', TaskUpdate.as_view(), name='task-update'),
        path('task/take/<str:task_id>/', take_task, name='task-take'),
        path('task/finish/<str:task_id>/', finish_task, name='task-finish'),    
        path('task/abort/<str:pk>/', abort_task, name='task-abort'),    
        path('task/cancel/<str:task_id>/', cancel_task, name='task-cancel'),
        path('task/remove/<str:task_id>/', remove_task, name='task-remove'), 
        path('task/archive/<str:task_id>/', archive_task, name='task-archive'),    
        path('task/wait/<str:task_id>/', add_listener, name='task-wait'),
        path('task/removewait/<str:task_id>/', remove_listener, name='task-removewait'),
        path('task/tow/<str:task_id>/', 
                TaskTakeOrWait.as_view(),
                name='task-take-or-wait'), 
]

