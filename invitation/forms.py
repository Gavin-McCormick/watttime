from django import forms
from django.conf import settings
import re


class InvitationKeyForm(forms.Form):
    first_name = forms.CharField(max_length=20)
    last_name = forms.CharField(max_length=20)
    email = forms.EmailField()
    sender_note = forms.CharField(widget=forms.Textarea, required=False, label='Your Note')
    
    def __init__(self, *args, **kwargs):
        self.remaining_invitations = kwargs.pop('remaining_invitations', None)
        self.user = kwargs.pop('user', None)
        self.invitation_blacklist = getattr(settings, 'INVITATION_BLACKLIST', ())
    
        super(InvitationKeyForm, self).__init__(*args, **kwargs)        
    
    def clean(self):
        cleaned_data = super(InvitationKeyForm, self).clean()

        if self.remaining_invitations <= 0:
            raise forms.ValidationError("Sorry, you don't have any invitations left")
        
        if 'email' in self.cleaned_data:
            if self.user.email == self.cleaned_data['email']:
                self._errors['email'] = self.error_class([u"You can't send an invitation to yourself"])
                del cleaned_data['email']
            
        if 'email' in self.cleaned_data:    
            for email_match in self.invitation_blacklist:
                if re.search(email_match, self.cleaned_data['email']) is not None:
                    self._errors['email'] = self.error_class([u"Thanks, but there's no need to invite us!"])
                    del cleaned_data['email']
                    break

        if 'sender_note' in self.cleaned_data:
            if not self.user.is_staff and len(cleaned_data['sender_note']) > 500:
                self._errors['sender_note'] = self.error_class([u"Your note must be less than 500 charicters"])
        
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        email = cleaned_data.get('email')
        
        if first_name and last_name and email:
            cleaned_data['recipient'] = (email, first_name, last_name )
        
        # Always return the cleaned data, whether you have changed it or
        # not.
        return cleaned_data
    