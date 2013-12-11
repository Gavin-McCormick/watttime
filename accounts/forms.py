from django import forms
from django_localflavor_us.us_states import STATE_CHOICES
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth import get_user_model
from django.utils.translation import ugettext, ugettext_lazy as _

from accounts import config

# DO NOT import accounts.models, including indirectly through other modules,
# as this module is imported by accounts.regions. See that file for explanation.

class UserProfileForm(forms.Form):
    name            = config.config_name.form_field
    password        = forms.CharField(help_text='Password', required = False)
    state           = config.config_state.form_field
    phone           = forms.CharField(help_text='Phone', required = False)
    equipment       = config.config_equipment.form_field
    beta_test       = config.config_beta_test.form_field
    ask_feedback    = config.config_ask_feedback.form_field

class SignupForm(forms.Form):
    email = forms.EmailField() #help_text='Email')
    state = forms.ChoiceField(choices = STATE_CHOICES) #, help_text='State')

    def __init__(self, *args, **kwargs):
        super(SignupForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = u'Email'

class LoginForm(forms.Form):
    email = forms.EmailField() #help_text='Email')
    password = forms.CharField( #help_text='Password',
            widget=forms.PasswordInput())

    def __init__(self, *args, **kwargs):
        super(LoginForm, self).__init__(*args, **kwargs)
        self.fields['email'].widget.attrs['placeholder'] = u'Email'
        self.fields['password'].widget.attrs['placeholder'] = u'Password'

class PhoneVerificationForm(forms.Form):
    verification_code = forms.IntegerField(label='Verification code')

class AccountCreateForm(forms.Form):
    name = forms.CharField() #help_text='Name')
    password = forms.CharField(#help_text='Password',
                               widget=forms.PasswordInput())
   # state = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')

    def __init__(self, *args, **kwargs):
        super(AccountCreateForm, self).__init__(*args, **kwargs)
        self.fields['name'].widget.attrs['placeholder'] = u'Name'
        self.fields['password'].widget.attrs['placeholder'] = u'Password'

class UserProfileFirstForm(forms.Form):
    phone = forms.CharField() #help_text='Phone')
   # state = forms.ChoiceField(choices = STATE_CHOICES, help_text='State')

    def __init__(self, *args, **kwargs):
        super(UserProfileFirstForm, self).__init__(*args, **kwargs)
        self.fields['phone'].widget.attrs['placeholder'] = u'Phone'
        
class PasswordResetWarningsForm(PasswordResetForm):
    error_messages = {
        'duplicate_email': _("Oops, there seems to be more than one user with that email! Please contact us to sort this out."),
        'missing_email': _("Hmm, couldn't find any users with that email. Try again?"),
        'unusable_password': _("Sorry, there's a problem with that account. Please contact us to sort this out."),
    }
    
    def clean(self, *args, **kwargs):
        # check for errors not caught by default form
        UserModel = get_user_model()
        email = self.cleaned_data["email"]    
        active_users = UserModel._default_manager.filter(email__iexact=email, is_active=True)
        if active_users.count() > 1:
            raise forms.ValidationError(self.error_messages['duplicate_email'],
                                        code='duplicate_email')
        elif active_users.count() == 0:
            raise forms.ValidationError(self.error_messages['missing_email'],
                                        code='missing_email')
        else:
            if not active_users[0].has_usable_password():
                raise forms.ValidationError(self.error_messages['missing_email'],
                                            code='missing_email')

        # run regular clean
        return super(PasswordResetWarningsForm, self).clean(*args, **kwargs)
