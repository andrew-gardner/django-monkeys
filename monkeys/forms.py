from django import forms
from registration.forms import RegistrationForm


class EmailFreeRegistrationForm(RegistrationForm):
    """
    Simply set the email field as non-required when registering
    a new user.
    """
    email = forms.EmailField(required=False)
