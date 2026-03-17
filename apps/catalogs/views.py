from django.shortcuts import render
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.views.generic.list import ListView
from .models import *
from .serializer import *
from .operate import *

# Create your views here.
class TaskCategoriesList(ListView):
    model = TCategory
    context_object_name = 'categories'
    template_name = 'task/task_category.html'

class TaskCategoryCreate(APIView):
    serializer_class = TaskCategorySerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_226_IM_USED)

class TaskSubCategoryCreate(APIView):
    serializer_class = TaskSubCategoryCreateSerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            try:
                subcat = TCategory()
                parent_name = serializer.data.get('parent_category')
                category_name = serializer.data.get('name')
                parent = TCategory.objects.get(name=parent_name)
                subcat.name = category_name
                subcat.parent = parent
                subcat.save()
                return Response(status=status.HTTP_201_CREATED)
            except:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_226_IM_USED)

class TaskCategoriesAll(APIView):
    alltask_categories = TCategory.objects.all()
    serializer_class = TaskSubCategorySerializer(alltask_categories,many=True)
    def get(self,request):
        return Response(self.serializer_class.data)

class ItemCategoryCreate(APIView):
    serializer_class = ItemCategorySerializer
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        return Response(status=status.HTTP_226_IM_USED)
