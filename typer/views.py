import os
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import DieImage, TypedDie

from django.conf import settings


def index(request):
    return HttpResponse("Hello, world. You're at the typer index.")


def detail(request, dieImage_id):
    """
    """
    di = get_object_or_404(DieImage, id=dieImage_id)
    return HttpResponse("""You're looking at die image %s.<br><br><img src="%s" /><br>""" % (dieImage_id, di.dieImage.url))
