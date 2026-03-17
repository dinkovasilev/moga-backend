from django.http import StreamingHttpResponse
from django.shortcuts import render
import asyncio
import random
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync, sync_to_async
from ..task.models import Task
from ..notifications.models import NType, Notifications, ChatRoom, ChatMessage
from django.contrib.auth.decorators import login_required

async def sse_stream(request):
    """
    Sends server-sent events to the client.
    """
    ch = get_channel_layer()
    await ch.group_send('group_msgTouser1',{'type':'notification','message':'Ново '})
    #group = request.GET.username
    async def event_stream():
        emojis = ["🚀", "🐎", "🌅", "🦾", "🍇"]
        i = 0
        while True:
            yield f'data: {random.choice(emojis)} {i}\n\n'
            i += 1
            await asyncio.sleep(1)
    return StreamingHttpResponse(event_stream(), content_type='text/event-stream')


def send_message(group,message):
    ch = get_channel_layer()
    ch.group_send(group,{'type':'notification','message':message})

def lobby(request, target_type, lobby_name):
    try:
        context={}
        info_group = []
        prefix = 'group_msgTo'
        sender = request.user
        target = None
        chatlog = None
        target_id = None
        print(f'Чат заявка пратена от: {sender.username}')
        if target_type == 'task':
            target = Task.objects.get(task_id=lobby_name)
            target_id = target.task_id
            chat_room, state = ChatRoom.objects.get_or_create(room_id=target_id)
            
            message = 'Чат: ' + target.category.name + ':' + target.name

            if target.personal:
                if not target.abandoned:
                    if sender != target.owner: 
                        info_group.append(target.owner.username)
                    for user in target.workers.all():
                        if sender == user: continue
                        info_group.append(user.username)

            

            ch = get_channel_layer()
            
            for user in info_group:
                if chat_room:
                    if user in chat_room.uname_list: continue
                Notifications.objects.create(destination=user,
                                             message=message,
                                             target_id=target_id,
                                             ntype=NType.chat.value)
                group = prefix + user
                async_to_sync(ch.group_send)(group,{'type':'chat','message':message,'target':target.task_id})
            
            chatlog = ChatMessage.objects.filter(target_id=target_id)
            longtext = ''
            for msg in chatlog:
                longtext += msg.to_string
        
        if chat_room:
            chat_room.users_in_room.add(sender)
            context['users_in_room'] = [usr.username for usr in chat_room.users_in_room.all()]
        context['lobby_name'] = lobby_name
        context['target'] = target
        if chatlog: context['chatlog'] = longtext
    except:
        print('срив на канала, съобщението не е пратено')

    return render(request,'notifications/lobby.html',context)

def notify(request,user_socket):
    return render(request,'home.html',{
        'recipient':user_socket
    })
