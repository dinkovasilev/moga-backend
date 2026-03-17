from django.urls import path
from .views import (
    TaskFilterCreate, 
    ItemFilterCreate,
    search_result,
    my_task_search_result,
)

urlpatterns = [
    path('task/filter/', TaskFilterCreate.as_view(), name='task-filter'),
    path('item/filter/', ItemFilterCreate.as_view(), name='item-filter'),
    path('search/',search_result,name='search'),
    path('search/my-space/',my_task_search_result,name='my-task-search')
    ]