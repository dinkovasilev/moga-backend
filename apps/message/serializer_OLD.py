from django import forms
from rest_framework import serializers
from ..message.models import Message
from ..player.operate import Choice

class SendMessageSerializer(serializers.Serializer):
    player = serializers.ChoiceField(
                choices=Choice.players())
    class Meta:
        fields = ['player']

class MessageForm(forms.ModelForm):
    class Meta:
        model = Message
        fields = ['message_text',]

class MobileMessageSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()
    def get_rating(self,obj):
        return obj.rating
    class Meta:
        model = Message
        fields = ['message_id', 'message_time', 'message_text', 'rating']
