from django import forms
from .models import TaskFilter, ItemFilter
from ..catalogs.operate import  ItemCategoryChoice, TaskSubCategoryChoice
from ..task.operate import TaskType, Status
from ..item.operate import ItemType, ItemStatus



default = [('Избери','Избери')]
task_type = TaskType.as_tupple()
task_type.remove(('БЕЛЕЖНИК','БЕЛЕЖНИК'))

class TaskFilterCreateForm(forms.ModelForm):
    category = forms.ChoiceField(
                            label='От категория',
                            choices= default + TaskSubCategoryChoice.as_tupple(),
                            initial='Избери категория',
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_category_list');",
                            }))
    task_type = forms.ChoiceField(
                            label='Тип на задачата',
                            choices= default + task_type,
                            initial='Избери тип',
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_mission_type');",
                            }))
    
    status = forms.ChoiceField(
                            label='Избери с какъв статус',
                            choices= default + Status.as_tupple(),
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_status_list');",
                            }))
    
    class Meta:
        model = TaskFilter
        fields = [
                    'task_type',
                    'mission_type',
                    'category',
                    'category_list',
                    'status',
                    'status_list',
                    'name_contains',
                    'description_contains',
                    'location_list',]

class ItemFilterCreateForm(forms.ModelForm):
    category = forms.ChoiceField(
                            label='От категория',
                            choices= default, # + ItemCategoryChoice.as_tupple(),
                            initial='Избери категория',
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_category_list');",
                            }))
    task_type = forms.ChoiceField(
                            label='Тип на задачата',
                            choices= default, # + ItemType.as_tupple(),
                            initial='Избери тип',
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_mission_type');",
                            }))
    
    status = forms.ChoiceField(
                            label='Избери с какъв статус',
                            choices= default + ItemStatus.as_tupple(),
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_status_list');",
                            }))
    
    class Meta:
        model = ItemFilter
        fields = [
                    'task_type',
                    'mission_type',
                    'category',
                    'category_list',
                    'status',
                    'status_list',
                    'name_contains',
                    'description_contains',
                    'location_list',]


"""category = forms.ModelChoiceField(
                            label='От категория',
                            queryset=TaskSubCategoryChoice.as_tupple(), #TCategory.objects.filter(parent=None),
                            widget=forms.Select(
                                attrs = {'onchange' : "update_field(this.value,'id_category_list');",
                            }))"""