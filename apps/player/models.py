from django.db import models
from django.contrib.auth.models import User
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

from enum import Enum
from PIL import Image
from ..tools.operate import *
from ..tools import properties
from ..task.models import Task
from ..task.operate import TaskType, Status
from ..item.models import Item
from ..item.operate import ItemType
from ..filters.models import TaskFilter, ItemFilter
from ..message.models import Message
from ..notifications.models import Notifications, NType


class PlayerStatus(Enum):
    ONLINE = 'ОНЛАЙН'
    OFFLINE = 'ОФЛАЙН'
    RELAXING = 'НЕ БЕЗПОКОЙ'
    MISSING = 'ОТСЪСТВА'
    INACTIVE = 'НЕАКТИВЕН'
    UNKNOWN = 'НЕИЗВЕСТЕН'

    def names_list():
        return [fieldname.name for fieldname in PlayerStatus]
    def values_list():
        return [fieldname.value for fieldname in PlayerStatus]
    def as_dict():
        return {f.value:f.name for f in PlayerStatus}
    def as_tupple():
        return [(f.value,f.name) for f in PlayerStatus]

class Player(models.Model):

    profile = models.OneToOneField(
                            User,
                            on_delete=models.CASCADE,
                            related_name='profile')
    player_id = models.CharField(
                            max_length=50,
                            primary_key=True)
    status = models.CharField(
                            verbose_name='Статус',
                            max_length=20, 
                            choices=PlayerStatus.as_tupple(),
                            default=PlayerStatus.UNKNOWN.value)
    missionbox = models.ManyToManyField(Task,related_name='missions')
    itembox = models.ManyToManyField(Item,related_name='itembox')
    
    updated = models.DateTimeField(null=True)
    banlist = models.ManyToManyField(User,related_name='banlist')

    def __str__(self):
        return f'{self.profile.username} Profile'
    

    def ban_reject(self, target:Task|Item):
        me = User.objects.get(username=self.profile.username)
        owner = Player.objects.get(player_id=target.player_id)
        return me in owner.banlist.all()
    ###################      messaging      ###################
    def push_message(self,target:object,text:str, image=None)->bool:
        no_text = (text == '' or text is None)
        no_image = (image == '' or image is None)
        if no_text and no_image: return False
        if isinstance(target,(Task,Item)): 
            boxes = [self.missionbox,self.itembox]
            proceed = False
            for box in boxes: 
                proceed = target in box.all()
                if proceed: break
            if not proceed: return False

            if target.personal:
                if self.ban_reject(target): return False
            
            message_id = ''
            while True:
                message_id = Id.generate(12)
                if Message.objects.filter(
                    message_id=message_id).count() == 0: break
            try:
                message = Message.objects.create(
                                            player=self.profile,
                                            message_id=message_id,
                                            message_text=text,
                                            image=image)
                if message.image:
                    pil_image = Image.open(message.image)
                    pil_image.thumbnail(properties.IMAGE_SIZE) #or resize
                    pil_image.save(message.image.path)
                    #print('IMAGE PATH: ', message.image.path)
                    pil_image.close()

                target.msgbox.add(message)
                
                return True
            except:
                return False
    def inbox(self):
        messages = dict()
        messages['Мисии'] = {task.name:{msg.player.username:msg.message_text 
                                        for msg in task.msgbox.all()}
                                        for task in self.missionbox.all()}
        messages['Искам'] = {item.name:{msg.player.username:msg.message_text 
                                        for msg in item.msbox.all()}
                                        for item in self.itembox.all()
                                        if item.item_type == ItemType.NEED.value}
        messages['Давам'] = {item.name:{msg.player.username:msg.message_text 
                                        for msg in item.msgbox.all()}
                                        for item in self.itembox.all()
                                        if item.item_type==ItemType.GIFT.value}
        return messages
    
    def get_posted_tasks(self):
        task_with_posts = []
        for task in self.missionbox.all():
            if task.msgbox.all().count() > 0:
                task_with_posts.append(task.task_id)
        posted_tasks = self.missionbox.filter(task_id__in=task_with_posts).order_by('created_on')
        return posted_tasks 
    def get_posted_items(self):
        item_with_posts = []
        allitems = list(self.itembox.all())
        for item in allitems:
            if item.msgbox.all().count()>0:
                item_with_posts.append(item.item_id)
        itembox = self.itembox.filter(item_id__in=item_with_posts)
        return list(itembox)
    def get_task_messages(self,task_id):
        task = Task.objects.get(task_id=task_id)
        messages = task.msgbox.all().order_by('message_time')
        for msg in messages:
            if msg.received(self.profile): continue
            msg.receive(self.profile)
        return messages
    def get_item_messages(self,item_id):
        item = Item.objects.get(item_id=item_id)
        messages = item.messages()
        for msg in messages:
            if msg.received(self.profile): continue
            msg.receive(self.profile)
        return messages
    def get_task_inbox(self):
        posted_tasks = self.get_posted_tasks()
        for task in posted_tasks:
            messages = task.msgbox.all()
            task.unread = 0
            for message in messages:
                if not message.received(self.profile):
                    task.unread += 1
        return posted_tasks
    def get_unread_item_messages(self):
        posted_items = self.get_posted_items()
        unread = {}
        for item in posted_items:
            messages = item.msgbox.all()
            unread[item.item_id] = 0
            for message in messages:
                if not message.received(self.profile):
                    unread[item.item_id] += 1
        return unread
    def notify_status(self,target:object,status:str)->None:
        if isinstance(target,Task): 
            message = self.profile.username + f' {status} ' + target.name + ' : ' + target.description
            prefix = 'group_msgTo'
            group = []

            if target.personal and not target.abandoned:
                group_name = prefix + target.owner.username
                Notifications.objects.create(destination=target.owner.username,
                                             message=message,
                                             target_id=target.task_id,
                                             ntype=NType.status.value)
                group.append(group_name)
            
            info_list = list(target.waiting_list.all()) + list(target.workers.all())
            for player in info_list:
                if player == self.profile: continue
                group_name = prefix + player.username
                Notifications.objects.create(destination=player.username,
                                             message=message,
                                             target_id=target.task_id,
                                             ntype=NType.status.value)
                group.append(group_name)

            ch = get_channel_layer()
            for member in group:
                async_to_sync(ch.group_send)(member,{'type':'notification','message':message})
                print('Статус съобщение до:', member)
    def notify_event(self)->None: ...

    ###################      missions      ###################
    def create_task(self,task_fields:dict):    
        task_id = ''
        while True:
            task_id = Id.generate(12)
            if Task.objects.filter(task_id=task_id).count() == 0: break
        task_fields['task_id'] = task_id
        task_fields['status'] = Status.INACTIVE.value
        task_fields['player_id'] = self.player_id
        try:
            task = Task(**task_fields)
            me = User.objects.get(username=self.profile.username)
            task.owner = me
            task.save()
            
            if task.task_type ==  TaskType.LESSON.value:
                task.waiting_list.add(me)
            if task.task_type ==  TaskType.DISCUSSION.value:
                task.workers.add(self.profile)
            if task.task_type != TaskType.PRIVATE.value:
                task.activate()
            else:
                task.capacity = 0
                task.save()
            self.missionbox.add(task)
            return True
        except: 
            task_fields['error'] = 'saving task and missionbox'
            return False
    def take_mission(self,task_id:str):
        try:
            task = Task.objects.get(task_id=task_id)
            
            if (task in self.missionbox.all()): return False
            if task.player_id == self.player_id: return False 
            if task.personal: 
                if self.ban_reject(task):return False 

            if task.enter(self.profile):
                self.missionbox.add(task)
                self.notify_status(task,'прие')
                return True
        except: return False
    def add_listener(self,task_id):
        task=None
        try:
            task = Task.objects.get(task_id=task_id)
            if task not in self.missionbox.all():
                self.missionbox.add(task)
            if self.profile not in task.waiting_list.all(): 
                if task.add_listener(self.profile):
                    return f'Добавен в списъка на {task.name}'
            else: return f'ти си в списъка на {task.name}'
        except:
            return f'Грешка при добавяне в списък с чакащи {task}'
    def abort_mission(self,task_id):
        try:
            task = Task.objects.get(task_id=task_id)
            if task.player_id != self.player_id: return False
            self.missionbox.remove(task)
            task.abort()
            self.notify_status(task,'ОТМЕНЯ')
            return True
        except:
            return {'error':'Player_abort_mission'}
    def archive_mission(self,task_id):
        try:
            task = Task.objects.get(task_id=task_id)
            if task.player_id != self.player_id: return False
            self.missionbox.remove(task)
            if task.workers_count > 0: return False
            if task.status != Status.COMPLETED.value: return False
            if not task.personal: return False
            if task.msgbox.count() > 0: task.archive()
            else: task.delete()
            return True
        except:
            return {'error':'Player_abort_mission'}
    def cancel_mission(self,task_id): 
        try:
            task = Task.objects.get(task_id=task_id)
            
            if task.player_id == self.player_id: 
                self.remove_mission(task_id)
                return True

            self.missionbox.remove(task)
            
            if self.profile not in task.workers.all(): return False

            task.leave(self.profile)

            self.notify_status(task,'напусна')

            if task.personal and task.workers_count == 0:
                task.msgbox.clear()
                if task.player_id == 'system':
                    task.delete()
            return True
        except:
            return {'error':'Player_cancel_mission'}
    # да се връща код на изпълнение за да се разпознава дали мисията е изтрита или само премахната от списъка
    def remove_mission(self,task_id):
        try:
            task = Task.objects.get(task_id=task_id)

            if task.player_id != self.player_id:return False

            if task.task_type == TaskType.LESSON.value:
                task.remove_listener(self.profile)
            if task.task_type == TaskType.DISCUSSION.value:
                task.workers.remove(self.profile)
            
            if task.personal and task.workers_count > 0:
                self.abort_mission(task.task_id)
            else: self.missionbox.remove(task)

            zero_players = task.workers_count == 0
            zero_waiters = task.listeners_count == 0
            
            if zero_players and zero_waiters: task.delete()
            else: 
                task.player_id = 'system'
                task.save(update_fields=['player_id',])
            return True
        except:
            return False
    def finish_mission(self,task_id): 
        try:
            task = Task.objects.get(task_id=task_id)
            if task.player_id != self.player_id:
                self.missionbox.remove(task)
                if self.profile in task.workers.all():
                    task.finish(self.profile)
                    self.notify_status(task,'завърши')
                    return True
            return False
        except:
            return {'error':'Player_cancel_mission'}
    def remove_listener(self,task_id): 
        try:
            task = Task.objects.get(task_id=task_id)
            self.missionbox.remove(task)
            task.remove_listener(self.profile)
            return True
        except:
            return False
    ###################      items      ###################
    def create_item(self,item_fields:dict): 
        item_id = ''
        while True:
            item_id = Id.generate(10)
            if Item.objects.filter(item_id=item_id).count() == 0: break
        item_fields['item_id'] = item_id
        item_fields['player_id'] = self.player_id
        item_fields['owner'] = User.objects.get(username=self.profile.username)
        item = Item(**item_fields)
        item.save()
        self.itembox.add(item)
    def take_delivery(self,item_id):
        try:
            item = Item.objects.get(item_id=item_id)
            
            is_vorbiden = self.profile in item.owner.banlist.all()
            if is_vorbiden: return False
            
            if (item.player_id == self.player_id): return False 
            
            if item.permit():
                self.itembox.add(item)
                item.start(self.profile)
                return True
            return False
        except: return False
    def cancel_delivery(self,item_id:str):
        try:
            item = Item.objects.get(item_id=item_id)
            
            if item.player_id == self.player_id: return False

            self.itembox.remove(item)
            item.restart()
            
            return True
        except:
            return False
    ###################  ban operations ###################
    def remove_itemhero(self,hero:User):
        for item in self.itembox.all():
            if hero == item.hero:
                item.restart()
    def remove_taskhero(self, worker:User):
        for mission in self.missionbox.all():
            if worker in mission.workers.all():
                mission.workers.remove(worker)
            if mission.workers_count == 0:
                mission.activate()
    #################  filter operations ##################
    def save_filter(self, filter_type:str, fields:dict):
        player_filter = None
        if filter_type == 'task':
            player_filter, _ = TaskFilter.objects.get_or_create(owner=self.profile)
        if filter_type == 'item':
            player_filter, _ = ItemFilter.objects.get_or_create(owner=self.profile)
        
        try:
            player_filter.clear_filter()
            for key in fields.keys():
                player_filter.__dict__[key] = fields[key]
            if bool(fields):
                player_filter.save(update_fields=list(fields.keys()))
            return True 
        except:
            return False
    ###################      other      ###################
    def update(self): self.updated = start_time()
    def check_hashes(self): 
        """
        за всички подобекти се генерира списък с хеш кодовете
        за фронтенда и бекенда след сравняване се прави актуализация
        ако е необходимо иначе само се сменя времето на полето updated
        """

    