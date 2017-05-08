from django import forms
from django.forms import Textarea
from .models import TypedDie

class MonkeyTyperForm(forms.ModelForm):
    class Meta:
        model = TypedDie
        fields = ['typedField']
        widgets = {
            'typedField': Textarea(attrs={'cols': 20, 'rows': 38}),
        }
