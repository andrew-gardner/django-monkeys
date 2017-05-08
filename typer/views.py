from django.http import HttpResponse
from django.shortcuts import render


def index(request):
    return HttpResponse("Hello, world. You're at the typer index.")


def detail(request, dieImage_id):
    return HttpResponse("You're looking at die image %s." % dieImage_id)
