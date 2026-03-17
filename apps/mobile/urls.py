from django.urls import path
from .views import (
    mobile_get_task_categories,
    mobile_get_task_messages,
    mobile_alltasks,
    mobile_mytasks,
    mobile_owntasks,
    mobile_subscribed_tasks,
    mobile_create_task,
    mobile_extern_tasks,
    mobile_task_action,
    mobile_message_vote,
    mobile_create_message,
)

urlpatterns = [
    path('mobile/freetasks/', mobile_alltasks,name='mobile-freetasks'),
    path('mobile/mytasks/', mobile_mytasks,name='mobile-mytasks'),
    path('mobile/owntasks/', mobile_owntasks,name='mobile-owntasks'),
    path('mobile/subscribed/', mobile_subscribed_tasks,name='mobile-subscribed'),
    path('mobile/task-categories/', mobile_get_task_categories,name='mobile-task-categories'),
    path('mobile/create-task/', mobile_create_task, name='mobile-create-task'),
    path('mobile/create-message/',mobile_create_message, name='mobile-create-message'),
    path('mobile/task-action/', mobile_task_action, name='mobile-task-action'),
    path('mobile/message-vote/', mobile_message_vote, name='mobile-message-vote'),
    path('mobile/extern-tasks/', mobile_extern_tasks, name='mobile-extern-task'),
    path('mobile/task-messages/<str:task_id>/', mobile_get_task_messages, name='mobile-task-messages'),
    ]