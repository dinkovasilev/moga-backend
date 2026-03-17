from django.db import models
from django.contrib.auth.models import User
from ..tools.operate import StringBox
from .operate import FilterFields

class FilterOptions(models.Model):
    class Meta: abstract=True

    mission_type = models.CharField(
                            verbose_name='Добавени типове',
                            max_length=20, 
                            null=True,
                            blank=True,
                            default='')
    created_after = models.DateTimeField(null=True,blank=True)
    category_list = models.CharField(
                            verbose_name='Избрани категории',
                            max_length=200,
                            null=True,
                            blank=True,
                            default='')
    status_list = models.CharField(
                            verbose_name='Статус:',
                            max_length=200, 
                            null=True,
                            blank=True,
                            default='')
    name_contains = models.CharField(
                            verbose_name='Наименованието да съдържа:',
                            max_length=200,
                            null=True,
                            blank=True,
                            default='')
    description_contains = models.CharField(
                            verbose_name='Описанието да съдържа:',
                            max_length=200,
                            null=True,
                            blank=True,
                            default='')
    location_list = models.CharField(
                            verbose_name='От район:',
                            max_length=200, 
                            null=True,
                            blank=True,
                            default='')
 
    def add_element(self,filter_field:str,element:str):
        self.__dict__[filter_field] = StringBox.add(self.__dict__[filter_field],element)
        self.save(update_fields=[filter_field,])
    def remove_element(self,filter_field:str,element:str):
        self.__dict__[filter_field] = StringBox.remove(self.__dict__[filter_field],element)
        self.save(update_fields=[filter_field,])
    def get_field_elements(self,box:str):
        return StringBox.get_elements(box)
    def clear_field(self,field:str):
        self.__dict__[field] = StringBox.clear()
        self.save(update_fields=[field,])
    def clear_filter(self):
        self.mission_type = None
        self.created_after = None
        self.category_list = None
        self.status_list = None
        self.name_contains = None
        self.description_contains = None
        self.location_list = None
        self.save(update_fields=FilterFields.FIELDS)
    
class ItemFilter(FilterOptions):
    owner = models.OneToOneField(
                            User,
                            on_delete=models.CASCADE,
                            related_name='itemfilter')
    def get_filter_data(self):
        filter_data = {}
        for field in FilterFields.FIELDS:
            if self.__dict__[field] is None: continue
            field_data = self.__dict__[field]
            field_reference = field.split('_')[0]
            if field_reference == 'created':
                filter_data[field_reference + '__gte'] = field_data
                continue
            if field_reference == 'mission':
                filter_data['item_type__in'] = self.get_field_elements(field_data)
                continue   
            if field_reference == 'description' or field_reference == 'name':
                filter_data[field_reference + '__contains'] = field_data
                continue 
            filter_data[field_reference + '__in'] = self.get_field_elements(field_data)                
        return filter_data

class TaskFilter(FilterOptions):
    owner = models.OneToOneField(
                            User,
                            on_delete=models.CASCADE,
                            related_name='taskfilter')
    def get_filter_data(self):
        filter_data = {}
        for field in FilterFields.FIELDS:
            if self.__dict__[field] is None: continue
            field_data = self.__dict__[field]
            field_reference = field.split('_')[0]
            if field_reference == 'created':
                filter_data[field_reference + '__gte'] = field_data
                continue
            if field_reference == 'mission':
                filter_data['task_type__in'] = self.get_field_elements(field_data)
                continue    
            if field_reference == 'description' or field_reference == 'name':
                filter_data[field_reference + '__contains'] = field_data
                continue
            filter_data[field_reference + '__in'] = self.get_field_elements(field_data)                
        return filter_data
