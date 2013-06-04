from django import forms
from django.forms.widgets import *
from django.core.mail import send_mail, BadHeaderError

# A simple contact form with four fields.
class ContactForm(forms.Form):
    name = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Name'}))
    email = forms.EmailField(label = "Email",
                           widget=forms.TextInput(attrs={'placeholder': 'Email'}))
    subject = forms.CharField(max_length=100,
                           widget=forms.TextInput(attrs={'placeholder': 'Subject'}))
    message = forms.CharField(widget=Textarea(attrs={'placeholder': 'Message'}))

