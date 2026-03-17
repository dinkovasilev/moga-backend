from rest_framework import serializers
from .models import *
from .operate import *

class customTaskSerializer:
    def create(fields):
        Meta = type('Meta', (object,), dict(model=Task, fields=fields))
        return type('TaskSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))

class TaskSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    class Meta:
        model = Task
        fields = [
                'status',
                'category_name',
                'task_id',
                'task_type',
                'name',
                'description',
                'capacity',
                'location',
                'valid_from',
                'valid_to',
                'general',]
    def get_category_name(self,obj):
        return obj.category.name

class MobileCreateTaskSerializer(serializers.Serializer):
    class Meta:
        model = Task
        fields = [
                'category',
                'task_type',
                'name',
                'description',
                'capacity',
                'location',
                'valid_from',
                'valid_to',
                #'general',
                ]