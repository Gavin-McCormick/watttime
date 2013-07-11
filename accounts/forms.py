from django import forms
from django_localflavor_us.us_states import STATE_CHOICES

import accounts.regions

class SignupForm(forms.Form):
    email = forms.CharField(help_text='Email')
    state = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = u'Email'

class LoginForm(forms.Form):
    email = forms.CharField(help_text='Email')
    password = forms.CharField(help_text='Password',
            widget=forms.PasswordInput(), required = False)

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = u'Email'
        self.fields['password'].widget.attrs['placeholder'] = u'Password'

class PhoneVerificationForm(forms.Form):
    verification_code = forms.IntegerField(label='Verification code')

class UserProfileFirstForm(forms.Form):
    password = forms.CharField(help_text='Password', widget=forms.PasswordInput())
    phone = forms.CharField(help_text='Phone')
    state = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')

    def __init__(self, *args, **kwargs):
        super(UserProfileFirstForm, self).__init__(*args, **kwargs)
        self.fields['password'].widget.attrs['placeholder'] = u'Password'
        self.fields['phone'].widget.attrs['placeholder'] = u'Phone'

# This form had to be in regions.py because it was needed there
UserProfileForm = accounts.regions.UserProfileForm

# This variable properly belongs here to go with UserProfileForm
EQUIPMENT_SHORT = accounts.regions.EQUIPMENT_SHORT
