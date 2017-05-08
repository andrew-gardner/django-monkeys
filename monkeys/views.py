from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from typer.models import Die


def HomeView(request):
    """
    """
    dieList = Die.objects.all()

    context = {
                  'dieList': dieList
              }
    return render(request, 'home.html', context)
