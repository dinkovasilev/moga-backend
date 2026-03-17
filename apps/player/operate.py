from enum import Enum
from .models import *

class PlayerFields:
    FIELDS = [
                'player_id',
                'status',
                'missionbox',
                'needsbox', 
                'giftsbox', 
                'waitingbox']

    def create():
        unwanted = {'missionbox', 'needsbox', 'giftsbox','waitingbox'}
        return [field for field in PlayerFields.FIELDS if field not in unwanted]
    def find():
        return PlayerFields.FIELDS
    def changestatus():
        unwanted = {'missionbox', 'needsbox', 'giftsbox','waitingbox'}
        return [field for field in PlayerFields.FIELDS if field not in unwanted]

class Destination(Enum):
    MYOWN = 'МОИ МИСИИ'
    EXTERN = 'ПОЕТИ МИСИИ'
    WAITING = 'ЛЕКЦИОНЕН СПИСЪК'
    def as_dict():
        return {f.value:f.name for f in Destination}


class Choice:
    def players(player_id:str=None):
        if player_id is not None:
            try:
                player = Player.objects.get(player_id=player_id)
                return {player.player_id:player.player_id}
            except: pass
        else:
            players = Player.objects.all()
            if players:
                return {player.player_id:player.player_id 
                        for player in players}
        return {'system':'empty'}

    def tasks(criteria:dict=None):
        if isinstance(criteria,dict):
            tasks = Task.objects.filter(**criteria)
            if tasks.exists():
                return {
                        task.task_id +':'+ 
                        task.name:task.task_id
                        for task in tasks}
        else: 
            tasks = Task.objects.all()
            if tasks.count()>0:
                return {
                        task.task_id +':' + 
                        task.category.name +':'+ 
                        task.name:task.task_id
                        for task in tasks}
        return {'system':'empty'}
