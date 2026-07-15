import json
import logging

from channels.generic.websocket import AsyncWebsocketConsumer
from .models import NType, Notifications, ChatRoom, ChatMessage
from ..task.models import Task
from ..item.models import Item
from ..player.models import Player

logger = logging.getLogger(__name__)


class NotifyConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_name = self.scope['url_route']['kwargs']['username']
        self.user_group_name = 'group_' + self.user_name
        await self.channel_layer.group_add(
            self.user_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send(text_data=json.dumps({
            'type':'status',
            'username':'server',
            'message':'Активирам известия'
        }))
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        uname = text_data_json['username']
        msgtype = text_data_json['type']

        if msgtype == 'notification':
            await self.channel_layer.group_send(
                self.user_group_name,{
                    'type':'notification',
                    'message': message,
                }
            )
        if msgtype == 'db_notifications_clear':
            await self.clear_notifications(uname, message)

        if msgtype == 'chat':
            target = text_data_json['target']
            await self.channel_layer.group_send(
                self.user_group_name,{
                    'type':'chat',
                    'message': message,
                    'target':target,
                }
            )
    async def chat(self,event):
        message = event['message']
        target = event['target']
        msgtype = event['type']
        data = json.dumps({
            'type':msgtype,
            'message': message,
            'target':target,
        })
        await self.send(text_data=data)
    async def notification(self, notification_event):
        message = notification_event['message']
        data = json.dumps({
            'message': message,
            'type':'notification'
        })
        await self.send(text_data=data)
    async def clear_notifications(self, username:str, target:str):
        match target:
            case 'all':
                await Notifications.objects.filter(destination=username).adelete()
            case _ :
                await Notifications.objects.filter(
                    destination=username).filter(
                        target_id=target).adelete()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.user_group_name,
            self.channel_name
        )

class ChatConsumer(AsyncWebsocketConsumer):
    http_user = True
    async def connect(self, **kwargs):
        self.lobby_name = self.scope['url_route']['kwargs']['lobby_name']
        self.lobby_group_name = 'group_' + self.lobby_name
        user = self.scope['user']
        target = None
        banlist = []
        try:
            match len(self.lobby_name):
                case 12:
                    target = await Task.objects.aget(task_id=self.lobby_name)
                    if target.personal:
                        owner = await Player.objects.aget(player_id=target.player_id)
                        banlist = [user async for user in owner.banlist.all()]
                case 10:
                    target = await Item.objects.aget(item_id=self.lobby_name)
                    owner = await Player.objects.aget(player_id=target.player_id)
                    banlist = [user async for user in owner.banlist.all()]

            if user in banlist:
                logger.info("Access denied to lobby %s for user %s", self.lobby_name, user)
                return

        except Exception:
            logger.exception("Failed to resolve lobby target %s", self.lobby_name)

        await self.channel_layer.group_add(
            self.lobby_group_name,
            self.channel_name
        )
        await self.accept()

        await self.send(text_data=json.dumps({
            'type':'connection_established',
            'username':'server',
            'message':'Успешно свързване'
        }))
        await self.channel_layer.group_send(
            self.lobby_group_name,{
                'type':'status_message',
                'username':user.username,
                'status': 'join',
                'message': 'влезе'
            }
        )
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json['username']
        sender = self.scope['user']

        if message == '': return

        await ChatMessage.objects.acreate(owner=sender,
                                          target_id=self.lobby_name,
                                          message=message)
        await self.channel_layer.group_send(
            self.lobby_group_name,{
                'type':'group_message',
                'message': message,
                'username':username,
            }
        )
    async def group_message(self, event):
        message = event['message']
        username = event['username']
        data = json.dumps({
            'message': message,
            'username':username,
        })
        await self.send(text_data=data)
    async def status_message(self, event):
        status = event['status']
        username = event['username']
        message = event['message']
        data = json.dumps({
            'status': status,
            'username':username,
            'message':message
        })
        await self.send(text_data=data)
    async def disconnect(self, close_code):
        user = self.scope['user']
        await self.channel_layer.group_send(
            self.lobby_group_name,{
                'type':'status_message',
                'username':user.username,
                'status': 'left',
                'message': 'напусна'
            }
        )
        await self.channel_layer.group_discard(
            self.lobby_group_name,
            self.channel_name
        )
        try:
            chat_room = await ChatRoom.objects.aget(room_id = self.lobby_name)
            await chat_room.users_in_room.aremove(user)
        except ChatRoom.DoesNotExist:
            logger.warning("Chat room %s not found on disconnect", self.lobby_name)
