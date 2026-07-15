import logging

from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import FormView
from django.urls import reverse, reverse_lazy
from django.http import HttpResponseRedirect
from django.contrib import messages
from .forms import CreateMessageForm
from ..player.models import Player
from ..task.models import Task,TaskType
from ..item.models import Item
from .serializer import *

logger = logging.getLogger(__name__)


class TaskCreateMessage(LoginRequiredMixin,FormView):
    template_name = 'task/task_message.html'
    form_class = CreateMessageForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('tasks-inbox')
    def get_context_data(self, **kwargs) -> dict:
        context = {}
        try:
            task = Task.objects.get(task_id=self.kwargs.get('task_id'))
            context['task'] = task
            context['form'] = self.form_class
        except Task.DoesNotExist:
            logger.warning("Task %s not found", self.kwargs.get('task_id'))
        return context
    def form_valid(self, form):
        task_id = self.kwargs.get('task_id')
        player_id = self.request.user.profile.player_id
        text = self.request.POST.get('message_text')
        image = self.request.FILES.get('image')
        player = Player.objects.get(player_id=player_id)
        target = Task.objects.get(task_id=task_id)
        self.success_url = reverse('task-messages',kwargs={'task_id':task_id})
        if target.personal:
            if player.ban_reject(target):
                messages.error(self.request,'Блокиран потребител')
                form.add_error(None, "Вашият акаунт е блокиран и не можете да подавате формуляра.")
                return self.form_invalid(form)
        if player.push_message(target,text,image):
            messages.success(self.request, "Съобщението е изпратено")
        else:
            messages.error(self.request,'Грешка при изпращане')
        return super(TaskCreateMessage, self).form_valid(form)
class ItemCreateMessage(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'item/item_message.html'
    pk_url_kwarg = 'item_id'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            item = Item.objects.get(item_id=self.kwargs.get('item_id'))
            context['item'] = item
        except Item.DoesNotExist:
            logger.warning("Item %s not found", self.kwargs.get('item_id'))
        return context

@csrf_exempt
@login_required
def task_save_message(request):
    if request.method=="POST":
        context=dict(request.POST.items()).keys()
        try:
            player_id = request.user.profile.player_id
            task_id = request.POST.get('task_id')
            text = request.POST.get('message_text')
            image = request.FILES.get('image')
            player = Player.objects.get(player_id=player_id)
            target = Task.objects.get(task_id=task_id)
            if target.personal:
                if player.ban_reject(target):
                    messages.error(request,'Блокиран потребител')
                    return HttpResponseRedirect(reverse('tasks-inbox'))
            
            if player.push_message(target,text,image):
                messages.success(request, "Съобщението е изпратено")
            else:
                messages.error(request,'Грешка при изпращане')
            return HttpResponseRedirect(reverse('task-messages',kwargs={'task_id':target.task_id}))
        except Exception:
            logger.exception("Failed to save task message")
            return render(request, 'error.html', {'ctx':context})
@csrf_exempt
@login_required
def item_save_message(request):
    if request.method=="POST":
        context=dict(request.POST.items()).keys()
        try:
            player_id = request.user.profile.player_id
            item_id = request.POST.get('item_id')
            text = request.POST.get('text')
            player = Player.objects.get(player_id=player_id)
            target = player.itembox.get(item_id=item_id)
            if player.profile in target.owner.banlist.all():
                messages.error(request,'Ти си блокиран от собственика на тази задача')
                return HttpResponseRedirect(reverse('items-inbox'))
            if player.push_message(target,text):
                messages.success(request, "Съобщението е изпратено")
                return HttpResponseRedirect(reverse('tasks-inbox'))
            else:
                context = [player.player_id,target.item_id]
                return render(request, 'error.html', {'ctx':context})
        except Exception:
            logger.exception("Failed to save item message")
            return render(request, 'error.html', {'ctx':context})

@csrf_exempt
@login_required
def message_up_vote(request, message_id, task_id):
    if request.method=="GET":
        context=dict(request.GET.items()).keys()
        try:
            message = Message.objects.get(message_id=message_id)
            if message.vote_up(request.user):
                messages.success(request,'Вота е приет')
            else:
                messages.warning(request, "Вота не е приет")
            return redirect(f'/task/messages/' + task_id)
        except Exception:
            logger.exception("Failed to process message vote")
            return render(request, 'error.html', {'ctx':context})
@csrf_exempt
@login_required
def message_down_vote(request, message_id, task_id):
    if request.method=="GET":
        context=dict(request.GET.items()).keys()
        try:
            message = Message.objects.get(message_id=message_id)
            if message.vote_down(request.user):
                messages.success(request,'Вота е приет')
            else:
                messages.warning(request, "Вота не е приет")
            return redirect(f'/task/messages/' + task_id)
        except Exception:
            logger.exception("Failed to process message vote")
            return render(request, 'error.html', {'ctx':context})