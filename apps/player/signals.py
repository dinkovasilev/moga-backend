from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Player
from ..tools.operate import Id

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        player_id = ''
        while True:
            player_id = Id.generate(10)
            if Player.objects.filter(player_id=player_id).count() == 0: break
        Player.objects.create(profile=instance,player_id=player_id)


@receiver(post_save, sender=User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()
