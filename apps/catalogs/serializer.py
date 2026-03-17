from rest_framework import serializers
from .models import *


from .operate import TaskCategoryChoice

class TaskCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = TCategory
        fields = ['name']

class MobileTCSerializer(serializers.ModelSerializer):
    subcategories = serializers.SerializerMethodField()
    class Meta:
        model = TCategory
        fields = ['id','name', 'subcategories']
    def get_subcategories(self, parent):
        #subcategories = parent.subcategories.all()
        if parent.subcategories.count()>0:
            return MobileTCSerializer(parent.subcategories.all(), many=True).data
        return None

    
class CustomTaskCategoriesSerializer:
    def create(fields):
        Meta = type('Meta', (object,), dict(model=TCategory, fields=fields))
        return type('TCategory', (serializers.ModelSerializer,), dict(Meta=Meta))

class TaskSubCategoryCreateSerializer(serializers.ModelSerializer):
    #parent_category = serializers.ChoiceField(choices=TaskCategoryChoice.cat_dict())
    parent_category = serializers.ChoiceField(choices=[])
    class Meta:
        model = TCategory
        fields = ['parent_category','name',]
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["parent_category"].choices = TaskCategoryChoice.cat_dict()
        
class TaskSubCategorySerializer(serializers.ModelSerializer):
    #category = serializers.RelatedField(source='category_name',read_only=True)
    category = serializers.CharField(source='task_category.category',read_only=True)
    class Meta:
        model = TCategory
        fields = ['name','parent',]





class ItemCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ICategory
        fields = ['name']
