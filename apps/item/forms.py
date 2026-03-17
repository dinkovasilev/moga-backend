from django import forms
from .models import Item
from .operate import ItemFields
from ..catalogs.operate import ItemCategoryChoice


default = ('default', 'default')


class ItemCreateForm(forms.ModelForm):
    _category_ = forms.ChoiceField(
        label='Категория',
        choices=[]
    )

    class Meta:
        model = Item
        fields = ['_category_']
        fields += ItemFields.on_create()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['_category_'].choices = ItemCategoryChoice.as_tupple()
