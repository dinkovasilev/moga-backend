from rest_framework import serializers
from .models import Item
from .operate import ItemCategoryChoices

class customItemSerializer:
    def create(fields):
        Meta = type('Meta', (object,), dict(model=Item, fields=fields))
        return type('ItemSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))

class ItemSerializer(serializers.ModelSerializer):
    category_ = serializers.ChoiceField(choices=ItemCategoryChoices.category())
    #_category_ = serializers.ChoiceField(choices=Choices.subcategory())
    class Meta:
        model = Item
        fields = [
                    'player_id',
                    'item_type',
                    'category_',
                    #'_category_',
                    'name',
                    'description',
                    'quantity',
                    'location',]
