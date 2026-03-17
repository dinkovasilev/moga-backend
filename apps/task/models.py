from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from .operate import TaskType, Status, TaskOptions
from ..tools.operate import *
from ..message.models import Message
from ..notifications.models import ChatMessage
from ..catalogs.models import TCategory

class Task(models.Model):
    """class Meta: unique_together = (('task_id','player_id'),)"""
            
    task_id = models.CharField(max_length=20,primary_key=True)
    player_id = models.CharField(max_length=20)
    owner = models.ForeignKey(
                            User,
                            on_delete=models.CASCADE,
                            related_name='task',
                            null=True, 
                            blank=True)
    created_on = models.DateTimeField(auto_now_add=True)
    task_type = models.CharField(
                            verbose_name='Тип на задачата',
                            max_length=20, 
                            choices=TaskType.as_tupple(),
                            default=TaskType.PRIVATE.value)
    """category = models.CharField(
                                verbose_name='Категория',
                                max_length=200,
                                default='Категория задачи',)"""
    category = models.ForeignKey(
                            TCategory,
                            on_delete=models.DO_NOTHING,
                            related_name='category',
                            null=True, 
                            blank=True,
                            verbose_name='Категория')
    name = models.CharField(
                            verbose_name='Заглавие',
                            max_length=200,
                            default='Няма заглавие')
    description = models.CharField(
                            verbose_name='Кратко описание',
                            max_length=200,
                            default='Без описание')
    status = models.CharField(
                            max_length=20, 
                            choices=Status.as_tupple(), 
                            default=Status.PENDING)
    capacity = models.IntegerField(
                            verbose_name='Необходими участници',
                            default=1)
    location = models.CharField(
                            verbose_name='Място на изпълнение',
                            max_length=200, 
                            default='България')
    valid_from = models.DateTimeField(
                            verbose_name='Валидна от',
                            editable=True,null=True,blank=True)
    valid_to = models.DateTimeField(
                            verbose_name='Валидна до',
                            default=deadline())
    workers = models.ManyToManyField(User, related_name='workers')
    waiting_list = models.ManyToManyField(User, related_name='listeners')
    msgbox = models.ManyToManyField(Message, related_name='task_post')
    unread = 0
    options = []
    general = models.BooleanField('Бедствие',default=False)
    
    @property
    def msg_count(self):
        return self.msgbox.all().count()
    @property
    def workers_count(self):
        return self.workers.all().count()
    @property
    def listeners_count(self):
        return self.waiting_list.all().count()
    @property
    def people(self):
        return self.workers_count + self.listeners_count
    @property
    def abandoned(self):
        if self.owner.profile.player_id == self.player_id: return False
        return True 
    @property
    def is_hidden(self):
        return self.task_type == TaskType.PRIVATE.value
    @property
    def task_age(self):
        return (timezone.now() - self.created_on).days
    @property
    def fullname(self):
        return (self.task_type + ' ' + 
                self.category.parent.name + ' ' +
                self.category.name + ' ' + 
                self.name + ' ' + 
                self.description).lower()
    @property
    def personal(self):
        if self.task_type == TaskType.LESSON.value: return False
        if self.task_type == TaskType.DISCUSSION.value: return False
        if self.general: return False
        return True
    
    def active_options(self,player:User):
        options = []
        if self.player_id == player.profile.player_id:
            options.append(TaskOptions.REMOVE.value)
            options.append(TaskOptions.EDIT.value)
            if self.task_type != TaskType.LESSON.value or self.msg_count > 0:
                options.append(TaskOptions.POST.value)
        else:
            match self.task_type:
                case TaskType.LESSON.value:
                    options.append(TaskOptions.LEAVE.value)
                    if player.profile in self.workers.all() or self.msg_count > 0:
                        options.append(TaskOptions.POST.value)
                case TaskType.DISCUSSION.value:
                    options.append(TaskOptions.CANCEL.value)
                    options.append(TaskOptions.POST.value)
                case TaskType.PRIVATE.value:
                    options.append(TaskOptions.REMOVE.value)
                    options.append(TaskOptions.EDIT.value)
                    options.append(TaskOptions.POST.value)
                case _:
                    if player.profile.ban_reject(self):
                        options.append(TaskOptions.UNSUBSCRIBE.value)
                    else:
                        options.append(TaskOptions.CANCEL.value)
                        options.append(TaskOptions.POST.value)
                        options.append(TaskOptions.FINISH.value)
        return list(set(options))
    
    def delete(self):
        try: 
            ChatMessage.objects.filter(target_id=self.task_id).delete()
            for msg in self.msgbox.all():
                msg.delete()
            super(Task, self).delete()
        except: super(Task, self).delete()

    def add_listener(self, player:User):
        if self.task_type == TaskType.LESSON.value:
            self.waiting_list.add(player)
            return True
        return False
    
    def remove_listener(self, player:User):
        self.waiting_list.remove(player)     

    def enter(self, player:User):  
        if self.is_hidden: return False
        if (self.general or 
            self.task_type==TaskType.DISCUSSION.value):
            self.capacity += 1 
        if self.workers_count == self.capacity: return False
        self.workers.add(player) 
        if self.status != Status.IN_PROCESS.value:
            self.start()    
        self.save(force_update=True)
        return True
    
    def leave(self, player:User):
        self.workers.remove(player)
        changestatus = (self.status == Status.IN_PROCESS.value or 
                        self.status == Status.PAUSED.value)
        if self.workers_count == 0 and changestatus: 
            self.status = Status.PENDING.value
        self.save()

    def abort(self): 
        self.status = Status.ABORTED.value
        self.valid_to = timezone.now()
        self.player_id = 'system'
        self.save()

    def archive(self): 
        self.status = Status.ARCHIVED.value
        self.valid_to = timezone.now()
        self.player_id = 'system'
        self.capacity = 0
        self.save()

    def finish(self, player:User): 
        self.valid_to = timezone.now()
        self.workers.remove(player)
        self.status = Status.COMPLETED.value
        self.save()

    def pause(self): 
        self.status = Status.PAUSED.value
        self.save()

    def activate(self): 
        self.status = Status.PENDING.value
        self.save()

    def deactivate(self): 
        self.status = Status.INACTIVE.value
        self.save()

    def start(self): 
        self.status = Status.IN_PROCESS.value
        self.save()
    
    def load(self):
        if self.personal:
            if self.capacity == 0: return 100 
            return round(self.workers_count/self.capacity,2)*100
        return 0    
    
