from django import forms
from .models import Task
from .operate import TaskFields
from ..catalogs.models import TCategory

class TaskCreateForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = TaskFields.on_create()
        widgets = {
            'valid_from': forms.widgets.DateTimeInput(attrs={'type':"datetime-local"},format=["%Y-%m-%d %H:%M:%S",]),
            'valid_to': forms.widgets.DateTimeInput(attrs={'type':"datetime-local"}),
        }


class TaskTakeForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = TaskFields.on_update()

class LoadTCategory(forms.Form):
    category = forms.ModelChoiceField(
        label='Област',
        queryset=TCategory.objects.filter(parent=None),
        widget=forms.Select(
            attrs = {'onchange' : "update_field(this.value,'category');"},
        ))
    
