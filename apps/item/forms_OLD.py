from django import forms
from .models import Item
from .operate import ItemFields
from ..catalogs.operate import ItemCategoryChoice

default = ('default','default')
class ItemCreateForm(forms.ModelForm):
    _category_ = forms.ChoiceField(
                            label='Категория',
                            choices=ItemCategoryChoice.as_tupple()
                            )
    class Meta:
        model = Item
        fields = ['_category_',]
        fields += ItemFields.on_create()




        
