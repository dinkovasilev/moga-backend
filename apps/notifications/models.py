from django.db import models
from django.contrib.auth.models import User

class NType(models.Choices):
    event = 'event'
    status = 'status'
    chat = 'chat'
    post = 'unread post'

class TargetType(models.Choices):
    item = 'item'
    task = 'task'
    unknown = 'unknown'

class MessageTemplate(models.Model):
    class Meta: abstract = True

    message = models.TextField(max_length=200,default='Здравей!')
    msgtime = models.DateTimeField(auto_now_add=True)
    target_id = models.CharField(max_length=20,null=True,default=None)

    @property
    def get_tmstring(self):
        return self.msgtime.strftime("%Y-%m-%d %H:%M:%S")
    @property
    def target_type(self):
        match len(self.target_id):
            case 12: return TargetType.task
            case 10: return TargetType.item
            case _: return TargetType.unknown

class Notifications(MessageTemplate):
    destination = models.CharField(max_length=50)
    ntype = models.CharField(max_length=200,
                             choices=NType,
                             null=True)
    

class ChatMessage(MessageTemplate):
    owner = models.ForeignKey(User,
                               on_delete=models.SET_NULL,
                               null=True, 
                               blank=True,
                               related_name='CHATS',
                               default=None)
    @property
    def to_string(self):
        return self.get_tmstring + ':[' + self.owner.username + ']:> ' + self.message + '\n'

class ChatRoom(models.Model):
    room_id = models.CharField(max_length=50,unique=True)
    users_in_room = models.ManyToManyField(User)

    @property
    def u_count(self):
        return self.users_in_room.count()
    @property
    def uname_list(self):
        return [usr.username for usr in self.users_in_room.all()]