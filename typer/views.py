import os
import re
import random
import logging

from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.models import User
from django.templatetags.static import static
from .models import Die, DieImage, TypedDie
from .forms import MonkeyTyperForm

logger = logging.getLogger(__name__)


def indexView(request, dieName):
    """
    This view displays a randomly choosen DieImage for a given Die.  Secret
    data about which die has been randomly chosen passes through to the POST
    method since this view decides it dynamically.

    Note:
    allAvailableFields = allAvailableFields.exclude(Q(dieImage=tuht.dieImage))
    Resulted in large AND NOT query after adding many entries
    Instead two separate queries and subtract out manually
    """
    userIsStaff = request.user.is_staff

    if request.method == 'GET':
        # Standard page display
        dieObject = Die.objects.filter(name=dieName)[0]
        allAvailableFields = TypedDie.objects.filter(Q(typedField="") & Q(dieImage__die=dieObject))

        thingsUserHasTyped = TypedDie.objects.filter(~Q(typedField="") & Q(submitter=request.user) & Q(dieImage__die=dieObject))
        setTyped = [td.dieImage_id for td in thingsUserHasTyped]
        usableFields = list(filter(lambda x: x.dieImage_id not in setTyped, allAvailableFields))
        #print 'avail', len(allAvailableFields)
        #print 'typed', len(setTyped)
        #print 'usable', len(usableFields)

        if not usableFields:
            return HttpResponse("<html><body>All fields have been typed for this die. Check back later to see if there are other dies to type.</body></html>")

        # Choose a random field to display
        randomField = random.randint(0, len(usableFields)-1)
        randomId = usableFields[randomField].id

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

        # Insure input is valid (if it is, data is stored in dieField, but not saved to the database)
        # TODO: There is a very good chance exceptions aren't being used correctly here
        if not form.is_valid():
            # Redisplay the same page but with an error message
            error = form.errors.as_data()['typedField'][0].message
            return imageInput(request, dieField.id, error, form.data['typedField'])

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
        # No need to update typedField since it's already saved in the is_valid() function call above
        dieField.save()

        # Return the next random page
        return HttpResponseRedirect(reverse('typer:index', kwargs={'dieName':dieName}))


def imageInput(request, fieldId, error=None, fieldData=None):
    """
    Helper function for the indexView - responsible for creating the page
    that features the input interface & possible error messages.
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

    # Prune off just the filename from the dieImage url
    dieImageBasename = os.path.basename(dieField.dieImage.image.url)

    # Display the input page
    context = {
                  'die': d,
                  'dieImage': di,
                  'dieImageBasename': dieImageBasename,
                  'typedDie': dieField,
                  'form' : form,
                  'error' : error,
              }
    return render(request, 'typer/imageInput.html', context)


def dieSpecificUserStatisticsView(request, dieName, userName):
    """
    A view that shows interesting statistics for the user specified in the url.
    """

    # If the given username isn't the logged-in user, see if it's staff.  If not, go no further.
    if userName != request.user.username and not request.user.is_staff:
        return HttpResponse("<html><body>Only administrators can access user statistics directly</body></html>")

    # Get the User object from the username
    dieObject = Die.objects.filter(name=dieName)[0]
    specifiedUser = None
    for user in User.objects.all():
        if userName == user.username:
            specifiedUser = user
    if specifiedUser is None:
        return HttpResponse("<html><body>The user %s does not exist.</body></html>" % userName)

    # Carry on
    userTypedTheseFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(submitter=specifiedUser))

    # How does this user's entry count compare to the others?
    userEntryTupleList = list()
    for user in User.objects.all():
        if user == specifiedUser:
            continue
        otherUserTypedFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(submitter=user))
        userEntryTupleList.append((user, len(otherUserTypedFields)))
    sortedByEntry = [x for (y,x) in sorted(userEntryTupleList, key=lambda pair: pair[1], reverse=True)]
    quantityRank = len(sortedByEntry)
    for i in range(len(sortedByEntry)):
        if len(userTypedTheseFields) > sortedByEntry[i]:
            quantityRank = i
            break
    quantityRank += 1

    # For each field the user typed, compare against other users' results
    comparisonMessages = list()
    for userTypedField in userTypedTheseFields:
        typedFieldCount = 0
        perfectMatchCount = 0
        allFieldsRelatedToUserTypedField = TypedDie.objects.filter(Q(dieImage=userTypedField.dieImage) & ~Q(submitter=specifiedUser))
        for field in allFieldsRelatedToUserTypedField:
            if field.completed():
                perfectMatchCount += 1 if (userTypedField.typedField == field.typedField) else 0
                typedFieldCount += 1
        # Construct a interesting message
        if typedFieldCount > 0:
            if perfectMatchCount == typedFieldCount:
                comparisonMessages.append("Your data matches the data everyone else typed for this image")
            elif perfectMatchCount != typedFieldCount:
                matchPercent = (float(perfectMatchCount) / float(typedFieldCount)) * 100.0
                comparisonMessages.append("Your data conflicts with what others typed.\nYou agree with %.0f%% of the others." % (matchPercent))
        else:
            comparisonMessages.append("You are the only one to type data for this image so far")

    # TODO: Low importance fix - if you're an admin and you 'typed the same image twice' this number is wrong
    allImagesForDie = DieImage.objects.filter(Q(die=dieObject))
    typedPercent = round(float(len(userTypedTheseFields)) / float(len(allImagesForDie)) * 100.0, 2)
    context = {
                  'die' : dieObject,
                  'typedCount' : len(userTypedTheseFields),
                  'typedPercent' : typedPercent,
                  'quantityRank' : quantityRank,
                  'specifiedUser' : specifiedUser,
                  'fieldsAndMessages' : zip(userTypedTheseFields, comparisonMessages)
              }
    return render(request, 'typer/userStatistics.html', context)


def dieInstructionsView(request, dieName):
    """
    A view that simply displays the instructions image and instruction text
    for the given Die.
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    instructions = dieObject.instructions

    # Find all the instances of images in our special markup [[[IMAGE_NAME (WIDTH HEIGHT)]]]
    m = re.finditer(r'\[\[\[(.*?)\]\]\]', instructions)
    for foundMatch in m:
        noBrackets = foundMatch.group(0).replace("[", "").replace("]", "")
        splitData = noBrackets.split()
        imageName = splitData[0]
        if len(splitData) > 1:
            imageWidth = int(splitData[1])
            imageHeight = int(splitData[2])
        imageObject = dieObject.instructionsimage_set.filter(Q(name=imageName))
        imageUrl = static(imageObject[0].image.url)
        if len(splitData) > 1:
            refText = """<img src="%s" width=%d height=%d>""" % (imageUrl, imageWidth, imageHeight)
        else:
            refText = """<img src="%s">""" % (imageUrl)
        instructions = instructions.replace(foundMatch.group(0), refText)

    # Copy the instructions back to a local die object (no database write)
    dieObject.instructions = instructions
    context = {
                  'die' : dieObject
              }
    return render(request, 'typer/instructions.html', context)


def adminStatisticsView(request, dieName):
    """
    """
    dieObject = Die.objects.filter(name=dieName)[0]

    # Get how many fields and how many have been typed
    allFields = TypedDie.objects.filter(Q(dieImage__die=dieObject))
    typedFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & ~Q(typedField=""))

    # Get a list of who's on first
    scoreboard = list()
    for user in User.objects.all():
        userTyped = TypedDie.objects.filter(~Q(typedField="") & Q(submitter=user) & Q(dieImage__die=dieObject))
        scoreboard.append( (user, len(userTyped)) )
    sortedScores = sorted(scoreboard, key=lambda tup: tup[1], reverse=True)

    context = {
                  'die' : dieObject,
                  'allFieldCount' : len(allFields),
                  'allTypedCount' : len(typedFields),
                  'scoreboard' : sortedScores
              }
    return render(request, 'typer/adminStatistics.html', context)


def adminSummaryHomeView(request, dieName):
    """
    An administrative view that displays a list of images and info about
    the typed information for each for the given Die.  The administrator
    can see how much data has been entered for each image and click on
    the image to open a new view showing more details.
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    allAvailableDieImages = DieImage.objects.filter(Q(die=dieObject))
    allApplicableTypedDies = TypedDie.objects.filter(Q(dieImage__die=dieObject))

    # Count all the entered fields for this die image (TODO: There must be a more Pythonic way to do this)
    totalFields = 0
    totalCompletedFields = 0
    dieIsCompleted = list()
    dieImageEntryCounts = list()
    # TODO: This is very slow right now - seems to be 2/3 python and 1/3 html - could be sped up with a Paginator
    for di in allAvailableDieImages:
        typedFields = allApplicableTypedDies.filter(Q(dieImage=di))
        completedFieldCount = 0
        for tf in typedFields:
            if tf.completed():
                completedFieldCount += 1
        totalFields += len(typedFields)
        totalCompletedFields += completedFieldCount
        dieImageEntryCounts.append(completedFieldCount)
        dieIsCompleted.append(completedFieldCount == len(typedFields))

    completedPercent = round(float(totalCompletedFields) / float(totalFields) * 100.0, 2)

    context = {
                  'die': dieObject,
                  'dieImageInfo': zip(allAvailableDieImages, dieImageEntryCounts, dieIsCompleted),
                  'completedPercent': completedPercent
              }
    return render(request, 'typer/adminSummaryHome.html', context)


def adminSummaryView(request, dieName, imageId):
    """
    This administrative view displays a summary of all the entered information
    for a given Die and DieImage.  One can also do rudimentary changes to the
    entered data and compare results.
    """
    dieObject = Die.objects.filter(name=dieName)[0]
    dieImage = DieImage.objects.filter(id=imageId)[0]
    allAvailableFields = TypedDie.objects.filter(Q(dieImage__die=dieObject) & Q(dieImage__id=imageId))

    if request.method == "POST":
        # Pull which clear button was pressed
        clearButtonsPressed = [k for k,v in request.POST.items() if k.startswith('clearButton')]
        if len(clearButtonsPressed) > 0:
            firstClearButtonPressed = clearButtonsPressed[0]
            clearNumberRe = re.search(r'(\d+)$', firstClearButtonPressed)
            clearNumber = int(clearNumberRe.group(0))
            workingField = allAvailableFields[clearNumber]

            # Clear the form
            workingField.submitter = None
            workingField.submitDate = None
            workingField.typedField = ""
            workingField.save()
            allAvailableFields[clearNumber].refresh_from_db()

        # Pull which save button was pressed
        saveButtonsPressed = [k for k,v in request.POST.items() if k.startswith('saveButton')]
        if len(saveButtonsPressed) > 0:
            firstSaveButtonPressed = saveButtonsPressed[0]
            saveNumberRe = re.search(r'(\d+)$', firstSaveButtonPressed)
            saveNumber = int(saveNumberRe.group(0))
            workingField = allAvailableFields[saveNumber]

            form = MonkeyTyperForm(request.POST, instance=workingField)
            if not form.is_valid():
                # TODO: Do something interesting here (really the admin should know better).
                #       As for now, it just reverts your changes.
                pass
            else:
                workingField.submitter = request.user
                workingField.submitDate = timezone.now()
                workingField.save()


    # Build the arrays that we want to display
    submitterArray = list()
    populatedForms = list()
    submitTimeArray = list()
    for aaf in allAvailableFields:
        populatedForms.append(MonkeyTyperForm(instance=aaf, initial={'typedField': aaf.typedField}))
        submitterArray.append(aaf.submitter)
        if aaf.submitDate:
            submitTimeArray.append(str(aaf.submitDate)[2:10] + "<br />" + str(aaf.submitDate)[12:16])
        else:
            submitTimeArray.append("N/A<br />N/A<br />")

    # Prune off just the filename from the dieImage url
    dieImageBasename = os.path.basename(dieImage.image.url)

    context = {
                  'die': dieObject,
                  'dieImage': dieImage,
                  'dieImageBasename': dieImageBasename,
                  'dieInfoArray': zip(populatedForms, submitterArray, submitTimeArray, range(len(submitTimeArray)))
              }

    return render(request, 'typer/adminSummaryView.html', context)

