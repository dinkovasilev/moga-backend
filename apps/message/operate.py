from enum import Enum
from ..task.models import Task
from ..item.models import Item

class MessageType(Enum):
    TASK = Task
    ITEM = Item

class MessageFields:
    FIELDS = ['player',
              'postbox',
              'message_id',
              'message_text',
              'message_time', 
              'deliverybox',
              'votersbox',
              'rating',]

    def on_create():
        unwanted = {'message_id',
                    'message_time', 
                    'deliverybox',
                    'votersbox',
                    'rating',}
        return [field for field in MessageFields.FIELDS if field not in unwanted]
    def on_get():
        return MessageFields.FIELDS
    def on_update():
        unwanted = {'player',
                    'postbox',
                    'message_id',
                    'message_time',}
        return [field for field in MessageFields.FIELDS if field not in unwanted]
    def on_delete():
        return ['message_id']




