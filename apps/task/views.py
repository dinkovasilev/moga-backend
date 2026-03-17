from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic.edit import FormView
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.shortcuts import redirect
from django.http import JsonResponse
from rest_framework import status
from rest_framework.parsers import JSONParser

from ..player.models import Player
from .models import Task
from .forms import TaskCreateForm, LoadTCategory
from ..catalogs.models import TCategory
from ..catalogs.serializer import MobileTCSerializer


def home(request):
    return render(request,'home.html')
  
class TaskCreate(LoginRequiredMixin,FormView):
    template_name = 'task/task_create.html'
    form_class = TaskCreateForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('owntasks')
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = TCategory.objects.filter(parent=None) #all().exclude(parent_isnull=False)
        serializer = MobileTCSerializer(categories,many=True)
        context['categories'] = serializer.data
        return context
    def form_valid(self, form):
        
        fields = {field:form.cleaned_data[field] 
                    for field in list(form.cleaned_data.keys()) 
                    if form.cleaned_data[field] is not None}
        try:
            categoryID = self.request.POST['category']
            category = TCategory.objects.get(pk=categoryID)
            fields['category'] = category

        except: pass
        try:
            player_id = self.request.user.profile.player_id
            player = Player.objects.get(player_id=player_id)
            player.create_task(fields)
        except: return render(self.request,'error.html')
        return super(TaskCreate, self).form_valid(form)
class TaskTakeOrWait(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task/task_take_or_wait.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
class TaskDetail(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task/task_detail.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            task = Task.objects.get(task_id=self.kwargs.get('task_id'))
            context['task'] = task
            context['taskmessages'] = player.get_task_messages(task.task_id)
        except:pass
        return context
class TaskActions(LoginRequiredMixin, DetailView):
    model = Task
    template_name = 'task/task_actions.html'
    context_object_name = 'task'
    pk_url_kwarg = 'task_id'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            task = Task.objects.get(task_id=self.kwargs.get('task_id'))
            context['task'] = task
            context['actions'] = task.active_options(player.profile)
        except:pass
        return context
class TaskUpdate(LoginRequiredMixin, UpdateView):
    model = Task
    fields = ['name','description','valid_from','valid_to','status']
    success_url = reverse_lazy('owntasks')
    template_name = 'task/task_update.html'
    def form_valid(self, form):
        messages.success(self.request, "Задачата е актуализирана.")
        return super(TaskUpdate,self).form_valid(form)
      
    def get_queryset(self):
        base_qs = super(TaskUpdate, self).get_queryset()
        return base_qs.filter(owner=self.request.user)
"""
# class TaskDelete(LoginRequiredMixin, DeleteView):
#     model = Task
#     context_object_name = 'task'
#     success_url = reverse_lazy('mytasks-list')
    
#     def form_valid(self, form):
#         messages.success(self.request, "Премахната")
#         return super(TaskDelete,self).form_valid(form)
      
#     def get_queryset(self):
#         base_qs = super(TaskDelete, self).get_queryset()
#         return base_qs.filter(owner=self.request.user)
"""    

# extract player object from database and return it to request function
def get_player(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if request.method == 'GET':
            try:
                player = Player.objects.get(profile=request.user)
                request.player = player
            except Player.DoesNotExist:
                return redirect('home')
            return view_func(request, *args, **kwargs)
        else: return redirect('home')
    return _wrapped_view

@login_required
@get_player
def take_task(request,task_id):
    try:
        if request.player.take_mission(task_id):
            messages.success(request, "Мисията е добавена в списъка")
        else:
            messages.error(request, "Не може да се изпълни")
        return redirect('externtasks')
    except: redirect('alltasks')

@login_required
@get_player
def cancel_task(request,task_id):
    try:
        if request.player.cancel_mission(task_id):
            messages.success(request, "Мисията е премахната от списъка")
        else:
            messages.error(request, "Не може да се изпълни")
    except: pass
    return redirect('mytasks-list')
@login_required
@get_player
def abort_task(request,task_id):
    try:
        if request.player.abort_mission(task_id):
            messages.success(request, "Премахната! Ако има участници ще ги уведомя!")
        else:
            messages.error(request, "Не може да се изпълни")
    except: messages.error(request, "Грешка")
    return redirect('mytasks-list')

@login_required
@get_player
def remove_task(request,task_id):
    try:
        if request.player.remove_mission(task_id):
            messages.success(request, "Мисията е премахната от списъка")
        else:
            messages.error(request, "Не може да се изпълни")
        return redirect('mytasks-list')
    except: return redirect('alltasks')

@login_required
@get_player
def add_listener(request,task_id):
    try:
        msg = request.player.add_listener(task_id)
        messages.success(request, msg)
        return redirect('waitingtasks')
    except: 
        return redirect('mytasks-list')

@login_required
@get_player
def remove_listener(request,task_id):
        try:
            if request.player.remove_listener(task_id):
                messages.success(request, "Лекцията е премахната от списъка")
            else:
                messages.error(request, "Не може да се изпълни")
        except: pass
        return redirect('mytasks-list')

@login_required
def archive_task(request,task_id):
    try:
        if request.player.archive_mission(task_id):
            messages.success(request, "Мисията е архивирана")
        else:
            messages.warning(request, "Премахната, но не е архивирана")
    except: messages.error(request, "Грешка в операцията")
    return redirect('mytasks-list')

@login_required
@get_player
def finish_task(request,task_id):
        try:
            if request.player.finish_mission(task_id):
                messages.success(request, "Мисията е премахната от списъка")
            else:
                messages.success(request, "Не може да се изпълни")
        except: messages.error(request, "Грешка в операцията")
        return redirect('externtasks')
         
@login_required
@get_player
def action(request,task_id):
    pass

