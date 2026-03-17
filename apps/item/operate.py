from enum import Enum


class ItemFields:    
    FIELDS = [
                'item_id',
                'player_id',
                'owner',
                'item_type',
                'created_on',
                'status',
                'category',
                'name',
                'description',
                'quantity',
                'location',
                'postbox',]

    def on_create():
        unwanted = {
                    'player_id',
                    'owner',
                    'category',
                    'postbox',
                    'item_id',
                    'created_on',}
        return [field for field in ItemFields.FIELDS if field not in unwanted]
    def on_get():
        return ItemFields.FIELDS
    def on_update():
        unwanted = {
                    "item_id",
                    "player_id",
                    "created_on",
                    "item_type",
                    "category",
                    "name",
                    "description",
                    "postbox"}
        return [field for field in ItemFields.FIELDS if field not in unwanted]
    def on_delete():
        return ['item_id']
     

class ItemStatus(Enum):
    NEW = 'НОВ'
    USED = 'УПОТРЕБЯВАН'
    GOOD = 'ДОБРО СЪСТОЯНИЕ'
    BAD = 'ЛОШО СЪСТОЯНИЕ'
    WASTED = 'ИЗНОСЕН'
    USEFULL = 'ГОДЕН'
    BROKEN = 'СЧУПЕН'
    ANY = 'БЕЗ ЗНАЧЕНИЕ'
    
    def names_list():
        return [fieldname.name for fieldname in ItemStatus]
    def values_list():
        return [fieldname.value for fieldname in ItemStatus]
    def as_dict():
        return {f.value:f.name for f in ItemStatus}
    def as_tupple():
        return [(f.value,f.value) for f in ItemStatus]
    
class ItemType(Enum):
    GIFT = 'ПОДАРЪК'
    NEED = 'ПОТРЕБНОСТ' 
    SERVICE = 'УСЛУГА' 

    def names_list():
        return [fieldname.name for fieldname in ItemType]
    def values_list():
        return [fieldname.value for fieldname in ItemType]
    def as_dict():
        return {f.value:f.name for f in ItemType}
    def as_tupple():
        return [(f.value,f.value) for f in ItemType]

"""
class ItemCategoryChoices:
    def category():
        category = ItemCategories.objects.all()
        if category.exists():
            return {cat.category_name:cat.category_name for cat in category}
        else:
            return {'system':'system'}
    def subcategory(category=None):
        if category is not None:
            subcategory = ItemSubCategories.objects.filter(category_name=category)
        else:
            subcategory = ItemSubCategories.objects.all()
        if subcategory.exists():
            return {subcat.__str__():subcat.__str__() for subcat in subcategory}

        else:
            return {'system':'system'}"""