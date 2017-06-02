from django import forms
from .models import TypedDie


class MonkeyTyperForm(forms.ModelForm):
    """
    """

    class Meta:
        model = TypedDie
        fields = ['typedField']
        widgets = {
            # TODO: Get values from database
            'typedField': forms.Textarea(attrs={'cols': 20, 'rows': 20})
        }


    def clean_typedField(self):
        """
        A validator for the typedField field that insures the field isn't blank
        and various other fun things.
        """
        data = self.cleaned_data['typedField']

        # TODO: Settings in the Models for which validators to use

        # Validation 0 : Insure there is some data present
        if not len(data.strip()):
            raise forms.ValidationError('No data present')

        # Validation 1 : Insure the data is binary only
        okChars = '01'
        for line in data.splitlines():
            allOk = all(c in okChars for c in line)
            if not allOk:
                raise forms.ValidationError('Invalid characters entered (just 0 and 1 please)')

        # Validation 2 : Insure the data is the proper width and height
        # TODO: Better validation using database info
        colCount = 0
        rowCount = len(data.splitlines())
        for line in data.splitlines():
            lineLen = len(line.strip())
            if not colCount:
                colCount = lineLen
            else:
                if colCount != lineLen:
                    raise forms.ValidationError('Bits entered horizontally do not match')

        return data
