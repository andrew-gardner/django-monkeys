from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import DieImage, TypedDie


def index(request):
    return HttpResponse("Hello, world. You're at the typer index.")


def detail(request, dieImage_id):
    """
    """
    di = get_object_or_404(DieImage, id=dieImage_id)

    typedDie = None
    for td in di.typeddie_set.all():
        if td.typedField == "":
            typedDie = td
            break

    if not typedDie:
        return HttpResponse("There are no more fields to fill for this die")

    context = {
                  'dieImage_id': dieImage_id,
                  'dieImage_url': di.dieImage.url,
                  'typedDie': typedDie
              }
    return render(request, 'typer/detail.html', context)
