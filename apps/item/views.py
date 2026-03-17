from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.views.generic.detail import DetailView
from django.views.generic.edit import UpdateView, DeleteView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.views.generic.edit import FormView

from ..player.models import Player
from .models import Item
from .forms import ItemCreateForm

class ItemCreate(LoginRequiredMixin,FormView):
    template_name = 'item/item_form.html'
    form_class = ItemCreateForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('ownitems')
    
    def form_valid(self, form):
        fields = {field:form.cleaned_data[field] 
                    for field in list(form.cleaned_data.keys()) 
                    if form.cleaned_data[field] is not None}
        if '_category_' in fields.keys(): fields['category'] = fields.pop('_category_')
        try:
            player_id = self.request.user.profile.player_id
            player = Player.objects.get(player_id=player_id)
            player.create_item(fields)
        except:
            context = dict(self.request.POST.items()).keys() 
            context = fields.values()
            return render(self.request,'error.html',{'ctx':context})
        return super(ItemCreate, self).form_valid(form)
class ItemDetail(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    pk_url_kwarg = 'item_id'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            item = Item.objects.get(item_id=self.kwargs.get('item_id'))
            context['item'] = item
        except:pass
        return context
class ItemUpdate(LoginRequiredMixin, UpdateView):
    model = Item
    fields = ['name','description','status']
    success_url = reverse_lazy('ownitems')
    
    def form_valid(self, form):
        messages.success(self.request, "Задачата е променена.")
        return super(ItemUpdate,self).form_valid(form)
      
    def get_queryset(self):
        base_qs = super(ItemUpdate, self).get_queryset()
        return base_qs.filter(owner=self.request.user)
class ItemDelete(LoginRequiredMixin, DeleteView):
    model = Item
    context_object_name = 'item'
    success_url = reverse_lazy('ownitems')
    
    def form_valid(self, form):
        messages.success(self.request, "Премахната")
        return super(ItemDelete,self).form_valid(form)
      
    def get_queryset(self):
        base_qs = super(ItemDelete, self).get_queryset()
        return base_qs.filter(owner=self.request.user)
class ItemTake(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'item/item_delivery.html'
    pk_url_kwarg = 'item_id'
    def get_context_data(self, **kwargs):
        context = {}
        try:
            item = Item.objects.get(item_id=self.kwargs.get('item_id'))
            context['item'] = item
        except:pass
        return context
class ItemDelivery(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'item/item_detail.html'
    pk_url_kwarg = 'item_id'

    def get_context_data(self, **kwargs):
        context = {}
        try:
            player = Player.objects.get(profile=self.request.user)
            item_id = self.kwargs.get("item_id")
            if player.take_delivery(item_id):
                messages.success(self.request, f"{item_id} Включена в списъка")
                context['item'] = player.itembox.get(item_id=self.kwargs.get("item_id"))
            else:
                messages.error(self.request, f"{item_id} Не може да се изпълни")
        except:
            messages.error(self.request, "Грешка в операцията")
        return context
class ItemCancel(LoginRequiredMixin, DetailView):
    model = Item
    context_object_name = 'item'
    template_name = 'item/item_detail.html'
    pk_url_kwarg = 'item_id'
    def get_object(self, queryset=None):
        try:
            player = Player.objects.get(profile=self.request.user)
            if player.cancel_delivery(self.kwargs.get("item_id")):
                messages.success(self.request, "Премахнат от списъка")
            else:
                messages.error(self.request, "Не може да се изпълни")
            return Item.objects.get(item_id=self.kwargs.get("item_id"))
        except:
            return render(self.request,'error.html')
