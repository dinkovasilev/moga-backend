import logging

from django.contrib.auth.models import User
from rest_framework.views import APIView
from django.views.generic.list import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render
from django.forms.models import model_to_dict
from rest_framework import status

import json
from django.http import JsonResponse
from rest_framework.parsers import JSONParser
from rest_framework.response import Response

import datetime

from ..task.models import Task
from ..task.serializer import TaskSerializer
from ..task.operate import TaskType

from ..catalogs.models import TCategory, ICategory
from ..catalogs.serializer import MobileTCSerializer

from ..message.models import Message
from ..message.serializer import MobileMessageSerializer
from ..item.models import Item
from ..filters.forms import TaskFilterCreateForm, ItemFilterCreateForm
from ..filters.models import TaskFilter, ItemFilter
from ..item.operate import ItemType
from ..task.serializer import MobileCreateTaskSerializer
from ..player.models import Player

logger = logging.getLogger(__name__)

########################## GET REQUESTS ####################################
@login_required
def mobile_alltasks(request):
    if request.method == 'GET':
        context={}
        try:
            player = Player.objects.get(profile=request.user)
            exclude_list = [task.task_id for task in player.missionbox.all()]

            context['tasks'] = Task.objects.all().exclude(
                task_id__in=exclude_list).exclude(
                    task_type=TaskType.PRIVATE.value)
            try:
                player_filter = TaskFilter.objects.get(owner=player.profile)
                filter_data = player_filter.get_filter_data()
                context['tasks'] = context['tasks'].all().filter(**filter_data)
                if bool(filter_data):
                    filter_form_object = TaskFilterCreateForm(data=model_to_dict(player_filter))
                    context['filter'] = filter_form_object
            except TaskFilter.DoesNotExist:
                pass
            serializer = TaskSerializer(context['tasks'],many=True)
            context['tasks'] = serializer.data
            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch all tasks for player")
        return JsonResponse({'error':'Error fetching all tasks list!'})

@login_required
def mobile_mytasks(request):
    if request.method == 'GET':
        context={}
        try:
            player = Player.objects.get(profile=request.user)
            context['tasks'] = player.missionbox.all()
            serializer = TaskSerializer(context['tasks'],many=True)
            context['tasks'] = serializer.data
            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch player's own tasks")
        return JsonResponse({'error':'Error fetching all tasks list!'})

@login_required
def mobile_owntasks(request):
    if request.method == 'GET':
        model = Task
        context={}
        try:
            player = Player.objects.get(profile=request.user)
            tasks = [task for task in player.missionbox.all().order_by('created_on')
                     if player.player_id == task.player_id]
            context['tasks'] = tasks
            context['heroes'] = {}
            for task in context['tasks']:
                if task.personal:
                    heroes = [user.username for user in task.workers.all()]
                    context['heroes'][task.task_id] = heroes
            serializer = TaskSerializer(context['tasks'],many=True)
            context['tasks'] = serializer.data
            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch player's created tasks")
        return JsonResponse({'error':'Error fetching all tasks list!'})

@login_required
def mobile_subscribed_tasks(request):
    if request.method == 'GET':
        context={}
        try:
            player = Player.objects.get(profile=request.user)
            missionbox = [task for task in player.missionbox.all()
                          if player.profile in task.waiting_list.all()]
            context['tasks'] = missionbox
            serializer = TaskSerializer(context['tasks'],many=True)
            context['tasks'] = serializer.data
            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch player's subscribed tasks")
        return JsonResponse({'error':'Error fetching all tasks list!'})

@login_required
def mobile_extern_tasks(request):
    if request.method == 'GET':
        context={}
        try:
            player = Player.objects.get(profile=request.user)
            missionbox = [task for task in player.missionbox.all()
                          if player.profile in task.workers.all()]
            context['tasks'] = missionbox
            serializer = TaskSerializer(context['tasks'],many=True)
            context['tasks'] = serializer.data
            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch player's external tasks")
        return JsonResponse({'error':'Error fetching all tasks list!'})

@login_required
def mobile_get_task_categories(request):
    if request.method == 'GET':
        context={}
        try:
            context['categories'] = TCategory.objects.filter(parent=None)

            serializer = MobileTCSerializer(context['categories'],many=True)
            context['categories'] = serializer.data

            return JsonResponse({'context':context})
        except Exception:
            logger.exception("Failed to fetch task categories")
        return JsonResponse({'error':'Error fetching task categories!'})

@login_required
def mobile_get_task_messages(request, task_id):
    if request.method == 'GET':
        context={}
        try:
            task = Task.objects.get(task_id=task_id)
            context['messages'] = task.msgbox.all()
            serializer = MobileMessageSerializer(context['messages'],many=True)
            context['messages'] = serializer.data
            return JsonResponse({'context':context})
        except Task.DoesNotExist:
            logger.warning("Task %s not found", task_id)
        return JsonResponse({'error':'Error fetching task messages!'})

########################################## POST REQUESTS ################################################

@csrf_exempt
@login_required
def mobile_task_action(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        response = {}
        try:
            taskID = data['target_id']
            action = data['action']
            player = Player.objects.get(profile=request.user)
            success = False
            match action:
                case 'add-listener':
                    success = player.add_listener(taskID)
                    response['message'] = 'Лекцията е добавена'
                case 'take-mission':
                    success = player.take_mission(taskID)
                    response['message'] = 'Мисията е приета'
                case 'leave-lesson':
                    success = player.remove_listener(taskID)
                    response['message'] = "Лекцията е премахната от списъка"
                case 'remove-note':
                    success = player.remove_mission(taskID)
                    response['message'] = "Бележника е премахнат"
                case 'cancel-task':
                    success = player.cancel_mission(taskID)
                    response['message'] = 'Мисията е отказана'
                case 'finish-task':
                    success = player.finish_mission(taskID)
                    response['message'] = 'Мисията е завършена'
            if success: return JsonResponse(response, status=status.HTTP_200_OK)
            response['message'] = 'Заявката не може да бъде изпълнена'
            return JsonResponse(response, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            logger.exception("Failed to process task action")
            return JsonResponse({"message": "Error in data"}, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@login_required
def mobile_message_vote(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        response = {}
        try:
            messageID = data['target_id']
            action = data['action']
            message = Message.objects.get(message_id=messageID)
            success = False
            match action:
                case 'vote-up':
                    success = message.vote_up(request.user)
                case 'vote-down':
                    success = message.vote_down(request.user)

            response['message'] = 'Вота е приет'
            response['rating'] = message.rating
            if success: return JsonResponse(response, status=status.HTTP_200_OK)
            response['message'] = 'Заявката не може да бъде изпълнена'
            return JsonResponse(response, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            logger.exception("Failed to process message vote")
            return JsonResponse({"message": "Error in data"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@login_required
def mobile_create_task(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        try:
            categoryID = data['category']
            category = TCategory.objects.get(pk=categoryID)
            data['category'] = category

            if data['location'] == '': data['location'] = 'България'
            if data['description'] == '': data['description'] = 'няма'
            serializer = MobileCreateTaskSerializer(data=data)
            if serializer.is_valid():
                player = Player.objects.get(profile=request.user)
                player.create_task(data)
                return JsonResponse({"message": "Task created successfully"}, status=status.HTTP_200_OK)
        except Exception:
            logger.exception("Failed to create task")
            return JsonResponse({"message": "Error in data"}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@csrf_exempt
@login_required
def mobile_create_message(request):
    if request.method == 'POST':
        data = JSONParser().parse(request)
        response = {}
        try:
            player_id = request.user.profile.player_id
            target_id = data['target_id']
            target_type = data['target_type']
            text = data['message']
            image = None
            player = Player.objects.get(player_id=player_id)
            match target_type:
                case 'task':
                    target = Task.objects.get(task_id=target_id)
                case 'item':
                    target = Item.objects.get(item_id=target_id)

            if target.personal:
                if player.ban_reject(target):
                    response['message'] = 'Блокиран потребител'
                    return JsonResponse(response, status=status.HTTP_401_UNAUTHORIZED)
            if player.push_message(target,text,image):
                response['message'] = 'Съобщението е изпратено'
                return JsonResponse(response, status=status.HTTP_200_OK)
            else:
                response['message'] = 'Грешка при изпращане'
                return JsonResponse(response, status=status.HTTP_403_FORBIDDEN)
        except Exception:
            logger.exception("Failed to create message")
    return JsonResponse({'message':'error posting message'}, status=status.HTTP_400_BAD_REQUEST)
