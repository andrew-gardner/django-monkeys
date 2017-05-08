import random

from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .models import Die, DieImage, TypedDie
from .forms import MonkeyTyperForm


def IndexView(request, dieName):
    """
    Given a particular die, get a list of all its
    DieImages, and choose one of those to present
    """

    if request.method != "POST":
        dieObject = Die.objects.filter(name=dieName)[0]
        allAvailableFields = TypedDie.objects.filter(Q(typedField="") | Q(typedField=None) & Q(dieImage__die=dieObject))
        if len(allAvailableFields) == 0:
            return HttpResponse("All fields have been typed for this die")
        randomField = random.randint(0, len(allAvailableFields)-1)
        randomId = allAvailableFields[randomField].id

        # TODO: Mutex lock
        return imageInput(request, randomId)

    else:
        # TODO: They say getting the data out of the request is bad form - fix
        form = MonkeyTyperForm(request.POST)
        typedText = request.POST['typedField']

        # Pull the previous die field out of the form's hidden data
        dieField = TypedDie.objects.filter(id=request.POST['dieField'])[0]

        # Good text in a POST?  Validate and save
        if typedText != "":
            if form.is_valid():
                dieField.submitter = request.user
                dieField.submitDate = timezone.now()
                dieField.typedField = typedText
                dieField.save()

                # Unlock the mutex

                # Return the next random page
                return HttpResponseRedirect('/typer/' + dieName)
        else:
            # Redisplay the same page but with an error message
            return imageInput(request, dieField.id, True)



def imageInput(request, fieldId, typedTextMissingError=False):
    """
    """
    # Recover the requested die image and its corresponding die
    dieField = get_object_or_404(TypedDie, id=fieldId)
    di = dieField.dieImage
    d = di.die

    # Display the input page
    context = {
                  'die': d,
                  'dieImage': di,
                  'typedDie': dieField,
                  'form' : MonkeyTyperForm,
                  'typedTextMissingError' : typedTextMissingError
              }
    return render(request, 'typer/imageInput.html', context)
