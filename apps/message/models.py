from django.db import models
from ..tools.operate import *
from django.contrib.auth.models import User

class Message(models.Model):
    parent = models.ForeignKey(
        "self",
        related_name="replies",
        on_delete=models.CASCADE,
        blank=True,
        null=True,
    )
    player = models.ForeignKey(User,
                               on_delete=models.CASCADE,
                               related_name='message'
                               )
    message_id = models.CharField(max_length=14,
                                  primary_key=True)
    message_text = models.TextField(verbose_name='Текст',
                                    max_length=7000,default='')
    message_time = models.DateTimeField(auto_now_add=True)
    delivery_list = models.ManyToManyField(User,related_name='recipients')
    image = models.ImageField(verbose_name='Снимка',
                                null=True, 
                                blank=True, 
                                upload_to='uploads/')
    upvotes = models.ManyToManyField(User,related_name='upvotes')
    downvotes = models.ManyToManyField(User,related_name='downvotes')

    def received(self,user:User)->bool:
        if user == self.player: return True
        if (user in self.delivery_list.all()): return True
        return False
    def receive(self,user:User):
        self.delivery_list.add(user)
    @property
    def votes(self)->int:
        return self.upvotes.count() + self.downvotes.count()
    @property
    def rating(self)->int:
        return self.upvotes.count() - self.downvotes.count()
    def vote_up(self,user:User)->bool:
        if user == self.player: return False
        if user in self.upvotes.all(): return False
        if user in self.downvotes.all(): 
            self.downvotes.remove(user)
        self.upvotes.add(user)
        return True
    def vote_down(self,user:User)->bool:
        if user == self.player: return False
        if user in self.downvotes.all():return False
        if user in self.upvotes.all():
            self.upvotes.remove(user)
        self.downvotes.add(user)
        return True


    

