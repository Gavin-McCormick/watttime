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

def signed_up(request):
    return render(request, 'pages/signed_up.html')

def signed_up_future(request):
    return render(request, 'pages/signed_up_future.html')

def faq(request):
#    return render(request, 'pages/placeholder.html', {'title': 'FAQ'})
    return render(request, 'pages/faq.html')

def about_us(request):
 #   return render(request, 'pages/placeholder.html', {'title': 'About WattTime'})
    return render(request, 'pages/about_us.html')

def how_it_works(request):
#    return render(request, 'pages/placeholder.html', {'title': 'How WattTime works'})
    return render(request, 'pages/how_it_works.html')

def terms_of_service(request):
#    return render(request, 'pages/placeholder.html', {'title': 'Terms of Service'})
    return render(request, 'pages/terms_of_service.html')

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

def thankyou(request):
    return render(request, 'pages/contact_thank_you.html')
