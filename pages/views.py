from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from models import ContactForm
from django.template import RequestContext
from django import forms
from django.forms.widgets import *
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from settings import EMAIL_HOST_USER

def server_error(request):
    return render(request, 'pages/500.html')

def notfound_error(request):
    return render(request, 'pages/404.html')

def status(request):
    user = request.user

    user_agent = request.META['HTTP_USER_AGENT']
    print ("User agent: {}".format(user_agent))
    is_internet_explorer = ('MSIE' in user_agent)

    if user.is_authenticated():
        initial_state = user.get_profile().state
    else:
        initial_state = 'CA'

    return render(request, 'pages/status.html',
            {'internet_explorer' : is_internet_explorer,
            'initial_state' : initial_state})

def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data

            try:
                send_mail(
                    cd['subject'],
                    cd['email'] + '\n' + cd['message'],
                    EMAIL_HOST_USER,
                    [EMAIL_HOST_USER]
                    )
                url = reverse('contact_thank_you')
                return HttpResponseRedirect(url)
            except BadHeaderError:
                return HttpResponse('Invalid header found.')
    else:
        form = ContactForm()

    return render(request, 'pages/contact.html', {'form':form})
