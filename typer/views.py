from django.utils import timezone
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, render
from .models import Die, DieImage, TypedDie
from .forms import MonkeyTyperForm


def index(request):
    return HttpResponse("Hello, world. You're at the typer index.")


def detail(request, dieImage_id):
    """
    """
    di = get_object_or_404(DieImage, id=dieImage_id)

    typedDie = None
    for td in di.typeddie_set.all():
        if td.typedField is None:
            typedDie = td
            break


    if request.method == 'POST':
        form = MonkeyTyperForm(request.POST)

        typedText = request.POST['typedField']
        if typedText == "":
            # TODO:
            print("NOTHING TO DO")

        typedDie.submitter = request.user
        typedDie.submitDate = timezone.now()
        typedDie.typedField = typedText
        typedDie.save()

        # Return the next random'ness
        return render(request, 'typer/detail.html')

    else:
        if not typedDie:
            return HttpResponse("There are no more fields to fill for this die")

        form = MonkeyTyperForm()
        print(form.Meta.model)

        context = {
                      'dieImage_id': dieImage_id,
                      'dieImage_url': di.image.url,
                      'typedDie': typedDie,
                      'form' : form
                  }
        return render(request, 'typer/detail.html', context)
