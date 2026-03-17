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
    destination = serializers.ChoiceField(choices=[])
    player = serializers.ChoiceField(choices=[])

    class Meta:
        fields = ['player', 'destination']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["destination"].choices = Destination.as_dict()
        self.fields["player"].choices = Choice.players()


class EnterWaitingSerializer(serializers.Serializer):
    player = serializers.ChoiceField(choices=[])
    task = serializers.ChoiceField(choices=[])

    class Meta:
        fields = ['player', 'task']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["player"].choices = Choice.players()
        self.fields["task"].choices = Choice.tasks(
            {'task_type': TaskType.LESSON.value}
        )
