import re
import random

from django.db.models import Q
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .models import Die, DieImage, TypedDie
from .forms import MonkeyTyperForm


def indexView(request, dieName):
    """
    Given a particular die, get a list of all its
    DieImages, and choose one of those to present
    """
    userIsStaff = request.user.is_staff

    if request.method != "POST":
        # Standard page display (no POST)
        dieObject = Die.objects.filter(name=dieName)[0]
        allAvailableFields = TypedDie.objects.filter(Q(typedField="") & Q(dieImage__die=dieObject))

        # Filter so that the same user never sees the same image twice eg. Q(user != self)
        if not userIsStaff:
            thingsUserHasTyped = TypedDie.objects.filter(~Q(typedField="") & Q(submitter=request.user))
            for tuht in thingsUserHasTyped:
                allAvailableFields = allAvailableFields.exclude(Q(dieImage=tuht.dieImage))

        # A simple message for users who have typed all there is to type
        # TODO: Make this more interesting
        if len(allAvailableFields) == 0:
            return HttpResponse("All fields have been typed for this die")

        # Choose a random field to display
        randomField = random.randint(0, len(allAvailableFields)-1)
        randomId = allAvailableFields[randomField].id

        # TODO: Mutex lock - maybe not needed
        return imageInput(request, randomId)

    else:
        # Data has been POSTed
        # TODO: They say getting the data out of the request is bad form - fix
        form = MonkeyTyperForm(request.POST)
        typedText = request.POST['typedField']

        # Pull the previous die field out of the form's hidden data
        dieId = int(request.POST['dieField'])
        dieField = TypedDie.objects.filter(id=dieId)[0]

        # Good text in a POST?  Validate and save
        if typedText != "":
            if form.is_valid():
                # TODO : Check if someone else has saved while you were working on this image
                #        If so, find another TypedDie that shares the same image to save to.
                dieField.submitter = request.user
                dieField.submitDate = timezone.now()
                dieField.typedField = typedText
                dieField.save()

                # TODO: Unlock the mutex - maybe not needed

                # Return the next random page
                return HttpResponseRedirect('/typer/' + dieName)
        else:
            # Redisplay the same page but with an error message
            return imageInput(request, dieField.id, True)


def imageInput(request, fieldId, typedTextMissingError=False):
    """
    Helper function for the indexView.
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


def summaryHomeView(request, dieName):
    """
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    allAvailableDieImages = DieImage.objects.filter(Q(die=dieObject))
    context = {
                  'die': dieObject,
                  'dieImages': allAvailableDieImages,
              }
    return render(request, 'typer/summaryHome.html', context)


def summaryView(request, dieName, imageId):
    """
    Displays a summary of all the entered information for a given
    Die and DieImage.
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    dieImage = DieImage.objects.filter(id=imageId)[0]
    allAvailableFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(dieImage__id=imageId))

    if request.method == "POST":
        # Pull which clear button was pressed
        buttonPressed = [ k for k,v in request.POST.items() if k.startswith('submitButton')][0]
        clearNumberRe = re.search(r'(\d+)$', buttonPressed)
        clearNumber = int(clearNumberRe.group(0))
        workingField = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(dieImage__id=imageId))[clearNumber]

        # Clear the form
        workingField.submitter = None
        workingField.submitDate = None
        workingField.typedField = ""
        workingField.save()
        allAvailableFields[clearNumber].refresh_from_db()

    # Build the arrays that we want to display
    submitterArray = list()
    populatedForms = list()
    submitTimeArray = list()
    for aaf in allAvailableFields:
        populatedForms.append(MonkeyTyperForm(initial={'typedField': aaf.typedField}))
        submitterArray.append(aaf.submitter)
        submitTimeArray.append(aaf.submitDate)

    context = {
                  'die': dieObject,
                  'dieImage': dieImage,
                  'typedDieArray': populatedForms,
                  'submitterArray': submitterArray,
                  'submitTimeArray': submitTimeArray,
                  'submitButtonNumbers': range(len(submitTimeArray))
              }

    return render(request, 'typer/summaryView.html', context)

