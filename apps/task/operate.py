from enum import Enum

class TaskFields:
    
    FIELDS = [
                'task_id',
                'user',
                'created_on',
                'task_type',
                'category',
                'name',
                'description',
                'status',
                'capacity',
                'location',
                'valid_from',
                'valid_to',
                'workers',
                'waiting_list',
                'general',
                'postbox',]

    def on_create():
        unwanted = {'waiting_list', 
                    'workers', 
                    'status',
                    'postbox',
                    'task_id',
                    'created_on',
                    'category',
                    'user',}
        return [field for field in TaskFields.FIELDS if field not in unwanted]
    def on_get():
        return TaskFields.FIELDS
    def on_update():
        unwanted = {
                    "task_id",
                    "user",
                    "created_on",
                    "task_type",
                    "category",
                    "name",
                    "description",
                    "capacity",
                    "postbox"}
        return [field for field in TaskFields.FIELDS if field not in unwanted]
    def on_delete():
        return ['task_id']
     
class Status(Enum):
    PENDING = 'ЧАКАЩА'
    IN_PROCESS = 'ПРОЦЕС'
    PAUSED = 'ПАУЗА'
    COMPLETED = 'ЗАВЪРШЕНА'
    ABORTED = 'ОТМЕНЕНА'
    INACTIVE = 'НЕАКТИВНА'
    ARCHIVED = 'АРХИВИРАНА'

    def names_list():
        return [fieldname.name for fieldname in Status if fieldname.name != 'ARCHIVED']
    def values_list():
        return [fieldname.value for fieldname in Status if fieldname.value != 'АРХИВИРАНА']
    def as_dict():
        return {f.value:f.name for f in Status if f.name != 'ARCHIVED'}
    def as_tupple():
        return [(f.value,f.name) for f in Status if f.name != 'ARCHIVED']
            
class TaskType(Enum):
    PRIVATE = 'БЕЛЕЖНИК'
    WORK = 'РАБОТА'
    SERVICE = 'УСЛУГА'
    DISCUSSION = 'ДИСКУСИЯ'
    LESSON = 'ЛЕКЦИЯ'
    BASIC = 'ДРУГИ'
    
    

    def names_list():
        return [fieldname.name for fieldname in TaskType]
    def values_list():
        return [fieldname.value for fieldname in TaskType]
    def as_dict():
        return {f.value:f.name for f in TaskType}
    def as_tupple():
        return [(f.value,f.value) for f in TaskType]

class TaskOptions(Enum):
    DELETE = 'DELETE'
    CANCEL = 'CANCEL'
    REMOVE = 'REMOVE'
    ABORT = 'ABORT'
    FINISH = 'FINISH'
    UNSUBSCRIBE = 'UNSUBSCRIBE'
    EDIT = 'EDIT'
    LEAVE = 'LEAVE'
    POST = 'POST'
    
