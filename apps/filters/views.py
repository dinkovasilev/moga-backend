from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic.edit import FormView
from django.views.decorators.csrf import csrf_protect, csrf_exempt
from django.contrib.auth.decorators import login_required

from ..task.models import Task, TaskType
from ..item.models import Item
from ..player.models import Player
from .forms import TaskFilterCreateForm, ItemFilterCreateForm


class TaskFilterCreate(LoginRequiredMixin,FormView):
    template_name = 'task_filter/taskfilter_form.html'
    form_class = TaskFilterCreateForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('alltasks')
    
    def form_valid(self, form):
        context=dict(self.request.POST.items()).keys()
        fields = {field:form.cleaned_data[field] 
                    for field in list(form.cleaned_data.keys()) 
                    if form.cleaned_data[field]}
        exclude_fields = ['category','task_type','status']
        for field in exclude_fields: 
            if field in fields.keys(): fields.pop(field)
        try:
            player_id = self.request.user.profile.player_id
            player = Player.objects.get(player_id=player_id)
            if player.save_filter('task',fields):
                messages.success(self.request,'Филтъра е запазен')
            return super(TaskFilterCreate, self).form_valid(form)
        except: 
            messages.error(self.request,'Филтъра не е създаден')
        values = [fields[key] for key in fields.keys()]
        return render(self.request,'error.html',{'ctx':values})
        
class ItemFilterCreate(LoginRequiredMixin,FormView):
    template_name = 'item_filter/itemfilter_form.html'
    form_class = ItemFilterCreateForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('allitems')
    
    def form_valid(self, form):
        context=dict(self.request.POST.items()).keys()
        fields = {field:form.cleaned_data[field] 
                    for field in list(form.cleaned_data.keys()) 
                    if form.cleaned_data[field]}
        exclude_fields = ['category','task_type','status']
        for field in exclude_fields: 
            if field in fields.keys(): fields.pop(field)
        try:
            player_id = self.request.user.profile.player_id
            player = Player.objects.get(player_id=player_id)
            if player.save_filter('item',fields):
                messages.success(self.request,'Филтъра е запазен')
            return super(ItemFilterCreate, self).form_valid(form)
        except: 
            messages.error(self.request,'Филтъра не е създаден')
        values = [fields[key] for key in fields.keys()]
        return render(self.request,'error.html',{'ctx':values})
    
@login_required    
def search_result(request):
    query = request.POST.get("search-query")
    context = {'query':query}
    if query:
        private = TaskType.PRIVATE.value
        query = str(query.lower())
        words = query.split()
        tasks = Task.objects.all().exclude(task_type=private)
        
        found = ''
        while words:
            word = words.pop(0)
            if len(word) <= 2: continue
            filtered_tasks = [task for task in tasks if word in task.fullname]#result.filter(fullname___icontains=word)
            if len(filtered_tasks) > 0:
                tasks = filtered_tasks
                found += word + ' '
        if found != '':
            context['tasks'] = tasks
            context['found'] = found
    return render(request,'search.html',context)

@login_required    
def my_task_search_result(request):
    query = request.POST.get("search-query")
    context = {'query':query}
    if query:
        player_id = request.user.profile.player_id
        player = Player.objects.get(player_id=player_id)
        print(player.profile.username, ' is requesting task')
        #private = TaskType.PRIVATE.value
        query = str(query.lower())
        words = query.split()
        tasks = player.missionbox.all()
        
        found = ''
        while words:
            word = words.pop(0)
            if len(word) <= 2: continue
            filtered_tasks = [task for task in tasks if word in task.fullname]#result.filter(fullname___icontains=word)
            if len(filtered_tasks) > 0:
                tasks = filtered_tasks
                found += word + ' '
        if found != '':
            context['tasks'] = tasks
            context['found'] = found
    return render(request,'search_my_space.html',context)