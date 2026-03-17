from django.db import models
from django.contrib.auth.models import User
from ..message.models import Message
from ..tools.operate import *
from .operate import ItemType, ItemStatus

class Item(models.Model):
    item_id = models.CharField(
                            max_length=12,
                            #default=Id.generate(12),
                            primary_key=True,
                            )
    owner = models.ForeignKey(
                            User,
                            on_delete=models.CASCADE,
                            related_name='item',
                            null=True, 
                            blank=True)
    player_id = models.CharField(max_length=10)
    item_type = models.CharField(
                            verbose_name='Тип',
                            max_length=20, 
                            choices=ItemType.as_tupple(),
                            default=ItemType.NEED.value)
    created_on = models.DateTimeField(auto_now_add=True)
    category = models.CharField(
                                verbose_name='Категория',
                                max_length=200,
                                #choices=ItemCategoryChoice.as_tupple(),
                                default='Категория предмети',)
    status = models.CharField(
                            verbose_name='Състояние',
                            max_length=20, 
                            choices=ItemStatus.as_tupple(), 
                            default=ItemStatus.GOOD)
    name = models.CharField(verbose_name='Какъв е',max_length=200,default='Няма название')
    description = models.CharField(verbose_name='Описание',max_length=200,default='Без описание')
    quantity = models.IntegerField(verbose_name='Количество',default=1,null=True)
    location = models.CharField(verbose_name='Локация',max_length=200, default='България')
    hero = models.ForeignKey(
                            User,
                            models.SET_NULL,
                            blank=True,
                            null=True,
                            related_name='hero')
    msgbox = models.ManyToManyField(Message)
    
    def delete(self):
        # calling parent relation to make cascade delete both

        super(Item, self).delete()
    def permit(self):    
        if self.item.hero == None:    
            return True
        return False
    def start(self, hero:User): 
        self.hero = hero
        self.save(update_fields=['hero',])
    def restart(self): 
        self.hero = None
        self.save(update_fields=['hero',])
    def is_private(self):
        return True
    def deliver(self): self.status = 'DELIVERED'
    def messages(self):
        return self.msgbox.all()