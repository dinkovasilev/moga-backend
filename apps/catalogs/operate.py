from .models import *



class TaskCategoryChoice:
    def cat_dict():
        categories = TCategory.objects.filter(parent=None)
        if categories.exists():
            return sorted({cat.name:cat.name 
                           for cat in categories})
        else: return {'system':'default'}
    def cat_tupple():
        categories = TCategory.objects.filter(parent=None)
        if categories.exists():
            return [(cat.name,cat.name) 
                    for cat in categories]
        else: return [('system','default')]
    def subcat_dict(catname:str):
        try:
            category = TCategory.objects.get(name=catname)
            return sorted({cat.name:cat.name 
                           for cat in category.subcategories.all()})
        except: return {'system':'default'}
        

class ItemCategoryChoice:
    def as_dict():
        categories = ICategory.objects.all()
        if categories.exists():
            return sorted({cat.name:cat.name
                           for cat in categories})
        else: return {'system':'default'}
    def as_tupple():
        categories = ICategory.objects.all()
        if categories.exists():
            return [(cat.name,cat.name) 
                    for cat in categories]
        else: return [('system','default')]


class TaskSubCategoryChoice:
    def as_tupple():
        subcategories = TCategory.objects.all().exclude(parent=None)
        if subcategories.exists():
            return [(cat.name,cat.name) 
                    for cat in subcategories]
        else: return [('system','default')]        
    
class ItemSubCategoryChoice:
    def as_tupple():
        subcategories = ICategory.objects.all()
        if subcategories.exists():
            return [(cat.__str__(),cat.__str__()) 
                    for cat in subcategories]
        else: return [('system','default')]