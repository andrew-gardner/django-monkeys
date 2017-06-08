from django import forms
from .models import TypedDie


class MonkeyTyperForm(forms.ModelForm):
    """
    """

    def __init__(self, *args, **kwargs):
        super(MonkeyTyperForm, self).__init__(*args, **kwargs)
        self.fields['typedField'].widget = forms.Textarea(attrs={'cols': self.instance.dieImage.bitWidth+2,
                                                                 'rows': self.instance.dieImage.bitHeight+2})

    class Meta:
        model = TypedDie
        fields = ['typedField']


    def clean_typedField(self):
        """
        A validator for the typedField field that insures the field isn't blank
        and various other fun things.
        """
        data = self.cleaned_data['typedField']

        # Remove whitespace from each line
        cleanedData = ""
        for line in data.splitlines():
            stripped = line.strip()
            if len(stripped) == 0:
                continue
            cleanedData += stripped
            cleanedData += "\n"

        # TODO: Settings in the Models for which validators to use

        # Validation 0 : Insure there is some data present
        if not len(cleanedData):
            raise forms.ValidationError('No data present')

        # Validation 1 : Insure the data is binary only
        okChars = '01?'
        for line in cleanedData.splitlines():
            allOk = all(c in okChars for c in line)
            if not allOk:
                raise forms.ValidationError('Invalid characters entered (just 0 and 1 please)')

        # Validation 2 : Insure the data is the proper number of bits in all dimensions
        colCount = 0
        rowCount = len(cleanedData.splitlines())
        bitWidth = self.instance.dieImage.bitWidth
        bitHeight = self.instance.dieImage.bitHeight
        if rowCount != bitHeight:
            raise forms.ValidationError('There are not enough rows of typed bits present - there should be %d' % bitHeight)
        for line in cleanedData.splitlines():
            lineLen = len(line.strip())
            if lineLen != bitWidth:
                raise forms.ValidationError('One or more rows does not have %d bits' % bitWidth)

        return cleanedData
