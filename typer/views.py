import re
import random
import logging

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from .models import Die, DieImage, TypedDie
from .forms import MonkeyTyperForm

logger = logging.getLogger(__name__)


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

        # Filter so that the same user never sees the same image twice eg. (submitter != self)
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

        # Display the random page
        return imageInput(request, randomId)

    else:
        # Data has been POSTed
        # Pull the previous die field out of the form's hidden data
        dieId = int(request.POST['dieField'])
        dieField = TypedDie.objects.filter(id=dieId)[0]
        someoneCompletedTheFieldBeforeYou = dieField.completed()

        # Create a form object from the post data and knowledge of which dieField we're dealing with
        form = MonkeyTyperForm(request.POST, instance=dieField)

        # Insure input is valid
        # TODO: There is a very good chance exceptions aren't being used correctly here
        if not form.is_valid():
            # Redisplay the same page but with an error message
            error = form.errors.as_data()['typedField'][0].message
            return imageInput(request, dieField.id, error, form.data['typedField'])

        # Gather the typed text
        typedText = form.cleaned_data['typedField']

        # If the strange situation occurred where someone snuck in and completed the field before you
        if someoneCompletedTheFieldBeforeYou:
            # TODO: Convert to django/Python logging
            dieObject = dieField.dieImage.die
            dieImageObject = dieField.dieImage
            print("User %s attempted to submit %s die image %s typed id %d, but someone else did first" %
                  (request.user,
                   dieObject,
                   dieImageObject,
                   dieId))

            # Find the next available dieField that is not completed
            availableFields = TypedDie.objects.filter(Q(typedField="") & Q(dieImage__die=dieObject) & Q(dieImage=dieImageObject))

            # If there is no place to squeeze the data in, just return the next random page
            if not len(availableFields):
                print("And there was no place free to put their work, so it got trashed")
                return HttpResponseRedirect('/typer/' + dieName)

            # If there is space, stuff it in the first object that's available
            print("So we are adding it to field %s instead" % dieField)
            dieField = availableFields[0]

        # Submit the user's input
        dieField.submitter = request.user
        dieField.submitDate = timezone.now()
        dieField.typedField = typedText
        dieField.save()

        # Return the next random page
        return HttpResponseRedirect(reverse('typer:index', kwargs={'dieName':dieName}))


def imageInput(request, fieldId, error=None, fieldData=None):
    """
    Helper function for the indexView.
    """
    # Recover the requested die image and its corresponding die
    dieField = get_object_or_404(TypedDie, id=fieldId)
    di = dieField.dieImage
    d = di.die

    # Populate the form with the raw data from the previous submit if there was an error
    if error and fieldData:
        form = MonkeyTyperForm(instance=dieField, initial={'typedField': fieldData})
    else:
        form = MonkeyTyperForm(instance=dieField)

    # Display the input page
    context = {
                  'die': d,
                  'dieImage': di,
                  'typedDie': dieField,
                  'form' : form,
                  'error' : error,
              }
    return render(request, 'typer/imageInput.html', context)


def dieInstructionsView(request, dieName):
    """
    """
    dieObject = Die.objects.filter(name=dieName)[0]

    context = {
                  'die' : dieObject
              }
    return render(request, 'typer/instructions.html', context)



def summaryHomeView(request, dieName):
    """
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    allAvailableDieImages = DieImage.objects.filter(Q(die=dieObject))

    # Count all the entered fields for this die image (TODO: There must be a more Pythonic way to do this)
    dieIsCompleted = list()
    dieImageEntryCounts = list()
    # TODO: This is very slow right now - a clever query should be able to get me the same info as this loop
    for di in allAvailableDieImages:
        typedFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(dieImage__id=di.id))
        completedFieldCount = 0
        for tf in typedFields:
            if tf.completed():
                completedFieldCount += 1
        dieImageEntryCounts.append(completedFieldCount)
        dieIsCompleted.append(completedFieldCount == len(typedFields))

    context = {
                  'die': dieObject,
                  'dieImageInfo': zip(allAvailableDieImages, dieImageEntryCounts, dieIsCompleted)
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
        populatedForms.append(MonkeyTyperForm(instance=aaf, initial={'typedField': aaf.typedField}))
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

