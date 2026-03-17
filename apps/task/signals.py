"""from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Task
from ..postbox.operate import PostBoxType
from ..tools.operate import Id"""
"""
@receiver(post_save, sender=User)
def create_task(sender, instance, created, **kwargs):
    if created:
        task_id = ''
        while True:
            task_id = Id.generate(12)
            if Task.objects.filter(task_id=task_id).count() == 0: break

        box = instance.profile.create_postbox(PostBoxType.TASK.value)
        Task.objects.create(
                            owner=instance,
                            task_id=task_id,
                            postbox=box)


@receiver(post_save, sender=User)
def save_task(sender, instance, **kwargs):
    instance.taskowner.save()"""
    

