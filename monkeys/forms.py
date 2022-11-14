import re

from django import forms
from django_registration.forms import RegistrationForm


class EmailFreeRegistrationForm(RegistrationForm):
    """
    Simply set the email field as non-required when registering
    a new user.
    """
    email = forms.EmailField(required=False)

    def clean_username(self):
        """
        Insure the username doesn't have any characters we don't want in it.
        """
        username = self.cleaned_data.get('username', '')
        badness = re.findall(r'[^a-zA-Z0-9\._@\-]', username)
        if len(badness):
            raise forms.ValidationError('Please keep user names to alphanumeric characters and the characters [. - _ @] only.')
        return username


class ContactForm(forms.Form):
    """
    A form layout for contacting the administrators of the site.
    """
    fromEmail = forms.EmailField(required=True, label="From e-mail")
    subject = forms.CharField(required=True, label="Subject")
    message = forms.CharField(widget=forms.Textarea(attrs={'cols': 70, 'rows': 10}), label="Message")
