import logging

from django.contrib.auth.models import User
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.views import View
from django.views.generic.edit import FormView
from django.views.generic.list import ListView
from django.contrib.auth.views import LoginView
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.forms.models import model_to_dict
from asgiref.sync import async_to_sync, sync_to_async
from channels.layers import get_channel_layer
import json

from ..task.models import Task
from ..task.operate import TaskType, Status
from ..message.models import Message
from ..item.models import Item
from ..filters.forms import TaskFilterCreateForm, ItemFilterCreateForm
from ..filters.models import TaskFilter, ItemFilter
from ..item.operate import ItemType
from .models import Player
from .forms import RegisterForm, UserUpdateForm
from .operate import PlayerFields
from .serializers import PlayerSerializer, UserSerializer

from django.views.decorators.csrf import ensure_csrf_cookie
from django.http import JsonResponse
from django.middleware.csrf import get_token
from django.contrib.auth.decorators import login_required

logger = logging.getLogger(__name__)

@ensure_csrf_cookie
def get_csrf_token(request):
    csrf_token = get_token(request)
    return JsonResponse({'csrfToken': csrf_token})

def get_auth_for_user(user):
	tokens = RefreshToken.for_user(user)
	return {
		'user': UserSerializer(user).data,
		'tokens': {
			'access': str(tokens.access_token),
			'refresh': str(tokens),
		}
	}

@csrf_exempt
def mobile_login(request):

    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            csrf_token = get_token(request)
            tokens = RefreshToken.for_user(user)
            user_data = {
                'user': UserSerializer(user).data,
                'tokens': {
                    'csrfToken':csrf_token,
                    'access': str(tokens.access_token),
                    'refresh': str(tokens),
                }
            }
            return JsonResponse(user_data)
        else:
            return JsonResponse({'error': 'Invalid credentials'}, status=400)


class MobileLoginView(APIView):
    def post(self, request, *args, **kwargs):

        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(username=username, password=password)

        if not user:
            return Response({'error': 'Невалиден логин'},status=401)

        csrf_token = get_token(request)
        tokens = RefreshToken.for_user(user)
        user_data = {
            'user': UserSerializer(user).data,
            'tokens': {
                'csrfToken':csrf_token,
                'access': str(tokens.access_token),
			    'refresh': str(tokens),
            }
        }
        return Response(user_data)


def home(request):
    return render(request,'home.html')
def content(request):
    return render(request,'content/content.html')

@csrf_exempt
@login_required
def profile(request):
    return render(request, 'player/profile.html')
@csrf_exempt
@login_required
def banlist(request):
    template_name = 'bans/ban_list.html'
    context = {}
    try:
        player = Player.objects.get(profile=request.user)
        context['bans'] = player.banlist.all()
    except Player.DoesNotExist:
        logger.warning("Player profile not found for user %s", request.user)
        return render(request,'home.html')
    return render(request,template_name,context)
@csrf_exempt
@login_required
def unblock_user(request, username):
    template_name = 'bans/ban_list.html'
    context = {}
    try:
        player = Player.objects.get(profile=request.user)
        user_to_unblock = User.objects.get(username=username)
        player.banlist.remove(user_to_unblock)
        context['bans'] = player.banlist.all()
    except Exception:
        logger.exception("Failed to unblock user %s", username)
        return render(request,'home.html')
    return render(request,template_name,context)
####################### CONTENT ######################
@csrf_exempt
@login_required
def publications(request):
    template_name = 'content/alldata.html'
    context = {'title':'Текущи беседи, дискусии, задачи и желания'}
    try:
        player = Player.objects.get(profile=request.user)
        alltasks = Task.objects.all()
        allitems = Item.objects.all()
        exclude_list = [task.task_id for task in player.missionbox.all()]
        context['tasks'] = list(alltasks.exclude(
                                task_id__in=exclude_list).exclude(
                                task_type=TaskType.PRIVATE.value))

        exclude_list = [item.item_id for item in player.itembox.all()]
        context['items'] = list(allitems.filter(hero=None).exclude(
            item_id__in=exclude_list))
    except Exception:
        logger.exception("Failed to load publications for user %s", request.user)
        return render(request,'home.html')
    return render(request,template_name,context)

####################### PROFILE ######################
class RegisterView(FormView):
    template_name = 'player/register.html'
    form_class = RegisterForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('owntasks')

    def form_valid(self, form):
        user = form.save()
        if user:
            login(self.request, user)

        return super(RegisterView, self).form_valid(form)
class MyLoginView(LoginView):
    template_name = 'player/login.html'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('owntasks')

    def form_invalid(self, form):
        messages.error(self.request,'Невалидно потребителско име или парола')
        return self.render_to_response(self.get_context_data(form=form))

class ChangeMail(LoginRequiredMixin, View):
    def get(self, request):
        user_form = UserUpdateForm(instance=request.user)
        context = {
            'user_form': user_form,
        }

        return render(request, 'player/change_mail.html', context)

    def post(self,request):
        user_form = UserUpdateForm(
            request.POST,
            instance=request.user
        )

        if user_form.is_valid():
            user_form.save()

            messages.success(request,'Your profile has been updated successfully')

            return redirect('profile')
        else:
            context = {
                'user_form': user_form,
            }
            messages.error(request,'Error updating you profile')

            return render(request, 'player/profile.html', context)
class PlayerChangeStatus(APIView):
    serializer_class = PlayerSerializer.create(PlayerFields.changestatus())
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            return Response(status=status.HTTP_404_NOT_FOUND)#ако е валиден значи това е месъществуващ играч
        player_id = serializer.data.get('player_id')
        receivedstatus = serializer.data.get('status')
        if player_id == "" or player_id is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            player = Player.objects.get(player_id=player_id)
            player.status = bool(receivedstatus)
            player.save(update_fields=['status'])
            player = Player.objects.get(player_id=player_id)
            response = {'ID':player.player_id,'status':player.status}
            return Response(response, status=status.HTTP_202_ACCEPTED)
        except Exception:
            logger.exception("Failed to change status for player %s", player_id)
            return Response(status=status.HTTP_304_NOT_MODIFIED)
####################### ITEMS ########################
@csrf_exempt
@login_required
def my_itembox(request):
    template_name = 'items/myitems_list.html'
    context = {}
    try:
        player = Player.objects.get(profile=request.user)
        context['items'] = player.itembox.all()
    except Player.DoesNotExist:
        logger.warning("Player profile not found for user %s", request.user)
        return render(request,'home.html')
    return render(request,template_name,context)
@csrf_exempt
@login_required
def my_needs(request):
    template_name = 'items/my_needs.html'
    context = {}
    try:
        player = Player.objects.get(profile=request.user)
        needs = player.itembox.filter(
            player_id=player.player_id
            ).filter(item_type=ItemType.NEED.value)
        services = needs = player.itembox.filter(
            player_id=player.player_id
            ).filter(item_type=ItemType.SERVICE.value)
        context['items'] = list(needs) + list(services)
    except Player.DoesNotExist:
        logger.warning("Player profile not found for user %s", request.user)
        return render(request,'home.html')
    return render(request,template_name,context)
class OwnItemList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'items'
    template_name = 'items/ownitem_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
            return context
        context['items'] = player.itembox.filter(owner=self.request.user)
        return context
class ExternItemList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'items'
    template_name = 'items/externitem_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
            return context
        my_gifts = player.itembox.filter(
            player_id=player.player_id
            ).filter(item_type=ItemType.GIFT.value)
        foreign_needs = player.itembox.filter(
            item_type=ItemType.NEED.value
            ).exclude(owner=self.request.user)
        service_needs = player.itembox.filter(
            item_type=ItemType.SERVICE.value
            ).exclude(owner=self.request.user)
        context['items'] = list(my_gifts) + list(foreign_needs) + list(service_needs)
        return context
class AllItemsList(LoginRequiredMixin, ListView):
    model=Item
    context_object_name = 'items'
    template_name = 'items/allitem_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        player = Player.objects.get(profile=self.request.user)
        exclude_list = [item.item_id for item in player.itembox.all()]
        untaken = Item.objects.filter(hero=None)
        context['items'] = untaken.all().exclude(item_id__in=exclude_list)
        try:
            player_filter = ItemFilter.objects.get(owner=player.profile)
            filter_data = player_filter.get_filter_data()
            context['items'] = context['items'].all().filter(**filter_data)
            if bool(filter_data):
                messages.success(self.request,'Има приложен филтър')
                filter_form_object = ItemFilterCreateForm(data=model_to_dict(player_filter))
                context['filter'] = filter_form_object
        except ItemFilter.DoesNotExist:
            pass
        return context

####################### TASKS ########################
class OwnTaskList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'tasks'
    template_name = 'tasks/owntask_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            tasks = [task for task in player.missionbox.all().order_by('created_on')
                     if player.player_id == task.player_id]
            context['tasks'] = tasks
            context['heroes'] = {}
            for task in context['tasks']:
                if task.personal:
                    heroes = [user.username for user in task.workers.all()]
                    context['heroes'][task.task_id] = heroes
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
        return context

class ExternTaskList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'tasks'
    template_name = 'tasks/externtask_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            missionbox = [task for task in player.missionbox.all()
                          if player.profile in task.workers.all()]
            context['tasks'] = missionbox
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
        return context

class WaitingTaskList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'tasks'
    template_name = 'tasks/waitingtask_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            tasks = [task for task in player.missionbox.all()
                     if player.profile in task.waiting_list.all()]
            context['tasks'] = tasks
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
        return context
class MyTasksList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/mytasks_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            context['tasks'] = player.missionbox.all().order_by('category')
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
        return context
class MyTasksChatList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/mytasks_chat_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            context['tasks'] = [task for task in player.missionbox.all().order_by('category')
                                if not task.is_hidden]
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
        return context
class AllTasksList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'tasks/alltask_list.html'
    form_class = TaskFilterCreateForm
    def get_context_data(self, **kwargs):
        player = Player.objects.get(profile=self.request.user)
        exclude_list = [task.task_id for task in player.missionbox.all()]
        context = super().get_context_data(**kwargs)
        context['tasks'] = context['tasks'].all().exclude(
            task_id__in=exclude_list).exclude(
                task_type=TaskType.PRIVATE.value).exclude(status=Status.COMPLETED.value)
        context['tasks'] = [task for task in context['tasks'] if task.load() < 100]
        try:
            player_filter = TaskFilter.objects.get(owner=player.profile)
            filter_data = player_filter.get_filter_data()
            context['tasks'] = context['tasks'].all().filter(**filter_data)
            if bool(filter_data):
                messages.info(self.request,'Има приложен филтър!')
                filter_form_object = TaskFilterCreateForm(data=model_to_dict(player_filter))
                context['filter'] = filter_form_object
        except TaskFilter.DoesNotExist:
            pass
        return context
####################### MESSAGES ########################
@csrf_exempt
@login_required
def inbox_list(request):
    context = {'title':'Списък на записите'}
    htmldoc = 'content/post_content.html'
    try:
        player = Player.objects.get(profile=request.user)
        context['tasks'] = player.get_task_inbox()
    except Player.DoesNotExist:
        logger.warning("Player profile not found for user %s", request.user)
    return render(request,htmldoc,context)

class TaskInboxList(LoginRequiredMixin, ListView):
    model = Task
    context_object_name = 'tasks'
    template_name = 'messages/task/task_inbox_list.html'
    def get_context_data(self, **kwargs):
        context = {'title':'Задачи с кореспонденция'}
        try:
            player = Player.objects.get(profile=self.request.user)
            context['tasks'] = player.get_task_inbox()
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
            context['tasks'] = player.missionbox.all()
        return context
class TaskMessageList(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'taskmessages'
    template_name = 'messages/task/task_message_list.html'
    def get_context_data(self, **kwargs):
        context = {'title':'Поща на задачите'}
        try:
            player = Player.objects.get(profile=self.request.user)
            context['tasks'] = player.get_posted_tasks()
            task_id = self.kwargs.get('task_id')
            context['task'] = Task.objects.get(task_id=task_id)
            context['taskmessages'] = player.get_task_messages(task_id)
        except Exception:
            logger.exception("Failed to load task message list for user %s", self.request.user)
        return context
class TaskHistory(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'taskmessages'
    template_name = 'messages/task/task_history.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            task_id = self.kwargs.get('task_id')
            context['task'] = Task.objects.get(task_id=task_id)
            context['taskmessages'] = player.get_task_messages(task_id)
        except Exception:
            logger.exception("Failed to load task history for user %s", self.request.user)
        return context
class ItemInboxList(LoginRequiredMixin, ListView):
    model = Item
    context_object_name = 'items'
    template_name = 'messages/item/item_inbox_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            context['items'] = player.get_posted_items()
            context['unread'] = player.get_unread_item_messages()
        except Player.DoesNotExist:
            logger.warning("Player profile not found for user %s", self.request.user)
            context['items'] = player.itembox.all()
        return context
class ItemMessageList(LoginRequiredMixin, ListView):
    model = Message
    context_object_name = 'itemmessages'
    template_name = 'messages/item/item_message_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            item_id = self.kwargs.get('item_id')
            context['item'] = Item.objects.get(item_id=item_id)
            context['items'] = player.get_posted_items()
            context['itemmessages'] = player.get_item_messages(self.kwargs.get('item_id'))
        except Exception:
            logger.exception("Failed to load item message list for user %s", self.request.user)
        return context
####################### BAN OPERATIONS ########################
class BanHero(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'bans'
    template_name = 'bans/ban_list.html'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            unwanted = User.objects.get(username=self.kwargs.get("username"))
            if unwanted:
                player.banlist.add(unwanted)
                player.remove_taskhero(unwanted)
                player.remove_itemhero(unwanted)
                messages.success(self.request, f"{unwanted.username} е блокиран")
            else:
                messages.warning(self.request, "Не може да се изпълни")
            context['bans'] = player.banlist.all()
        except Exception:
            logger.exception("Failed to ban user %s", self.kwargs.get("username"))
            messages.error(self.request,'Грешка в операцията')
        return context
