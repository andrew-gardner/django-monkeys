from django import forms
from registration.forms import RegistrationForm


class EmailFreeRegistrationForm(RegistrationForm):
    """
    Simply set the email field as non-required when registering
    a new user.
    """
    email = forms.EmailField(required=False)


class ContactForm(forms.Form):
    """
    A form layout for contacting the administrators of the site.
    """
    fromEmail = forms.EmailField(required=True, label="From e-mail")
    subject = forms.CharField(required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 70, 'rows': 10}), label="Message")
