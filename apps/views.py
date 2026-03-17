from django.shortcuts import render
from .catalogs.models import TCategory
from .catalogs.serializer import MobileTCSerializer
import json

def index(request):
    return render(request,'templates/index.html')

def json_test_view(request):
    context = {}
    try:
            categories = TCategory.objects.filter(parent=None) #all().exclude(parent_isnull=False)
            serializer = MobileTCSerializer(categories,many=True)
            #context['categories'] = json.dumps(serializer.data, sort_keys=True, ensure_ascii=False )
            context['categories'] = serializer.data
    except: pass
    return render(request, 'templates/play_ground.html', context)