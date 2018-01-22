from datetime import date
from django import forms


class AuthorizationForm(forms.Form):
    key = forms.EmailField(max_length=254, help_text="Required. Input a valid email address.")
    secret = forms.CharField(max_length=32, widget=forms.PasswordInput)


class SalesForm(forms.Form):
    # not used for validation in views :(
    date_from = forms.DateField(input_formats='YYYY-mm-dd', initial=date(2015, 11, 17))
    date_to = forms.DateField(input_formats='YYYY-mm-dd', initial=date(2015, 11, 18))
