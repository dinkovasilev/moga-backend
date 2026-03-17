from rest_framework import serializers
from .models import Player, User
from .operate import *


class UserSerializer(serializers.ModelSerializer):
	name = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = [
			'username',
			'name',
		]

	def get_name(self, obj):
		fname = obj.first_name.capitalize()
		lname = obj.last_name.capitalize()
		return fname + ' ' + lname



class PlayerSerializer:
    def create(fields):
        Meta = type('Meta', (object,), dict(model=Player, fields=fields))
        return type('PlayerSerializer', (serializers.ModelSerializer,), dict(Meta=Meta))

class PlayerMissionsSerializer(serializers.Serializer):
    destination = serializers.ChoiceField(
                    choices=Destination.as_dict())
    player = serializers.ChoiceField(
                choices=Choice.players())
    class Meta:
        #model = Player
        fields = ['player','destination']
       
class EnterWaitingSerializer(serializers.Serializer):
    player = serializers.ChoiceField(
                choices=Choice.players())
    task = serializers.ChoiceField(
            choices=Choice.tasks(
                {'task_type':TaskType.LESSON.value}))
    class Meta:
        #model = Player
        fields = ['player','task']

# class TakeTaskSerializer(serializers.Serializer):
#     player = serializers.ChoiceField(
#                 choices=Choice.players())
#     task = serializers.ChoiceField(
#             choices=Choice.tasks())
#     class Meta:
#         #model = Player
#         fields = ['player','task']