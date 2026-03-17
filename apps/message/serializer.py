from django import forms
from rest_framework import serializers
from ..message.models import Message
from ..player.operate import Choice


class SendMessageSerializer(serializers.Serializer):
    player = serializers.ChoiceField(choices=[])

    class Meta:
        fields = ['player']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["player"].choices = Choice.players()


class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_text']


class MobileMessageSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj):
        return obj.rating

    class Meta:
        model = Message
        fields = ['message_id', 'message_time', 'message_text', 'rating']
