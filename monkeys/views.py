from django.core.mail import send_mail, BadHeaderError
from django.http import HttpResponse
from django.shortcuts import render, redirect
from typer.models import Die
from .forms import ContactForm


def homeView(request):
    """
    """
    dieList = Die.objects.all()

    context = {
                  'dieList': dieList
              }
    return render(request, 'home.html', context)


def contactView(request):
    """
    """
    submitSuccess = False
    if request.method == 'GET':
        form = ContactForm()
    else:
        form = ContactForm(request.POST)
        if form.is_valid():
            fromEmail = form.cleaned_data['fromEmail']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            message = "From user : " + str(request.user.username) + "\n\n" + ("-" * 40) + "\n\n" + message

            # Send the mail
            try:
                send_mail(subject, message, fromEmail, ['chowderq@yahoo.com'])
            except BadHeaderError:
                return HttpResponse('Invalid e-mail header found.')
            submitSuccess = True

    context = {
                  'form' : form,
                  'submitSuccess' : submitSuccess
              }
    return render(request, 'contact.html', context)
