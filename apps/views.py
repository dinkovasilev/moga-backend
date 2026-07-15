import logging

from django.shortcuts import render
from .catalogs.models import TCategory
from .catalogs.serializer import MobileTCSerializer

logger = logging.getLogger(__name__)


def index(request):
    return render(request, 'templates/index.html')


def json_test_view(request):
    context = {}
    try:
        categories = TCategory.objects.filter(parent=None)
        serializer = MobileTCSerializer(categories, many=True)
        context['categories'] = serializer.data
    except Exception:
        logger.exception("Failed to load categories for play_ground view")
    return render(request, 'templates/play_ground.html', context)