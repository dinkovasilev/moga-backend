from django.urls import path
from .views import *

urlpatterns = [
    path('item/category/create/',ItemCategoryCreate.as_view()),
    path('task/category/create/',TaskCategoryCreate.as_view()),
    path('task/subcategory/create/',TaskSubCategoryCreate.as_view()),
    path('task/subcategory/all/',TaskCategoriesAll.as_view()),
    path('task/categories/',TaskCategoriesList.as_view(),name='task-category-list'),
]
