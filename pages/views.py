from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from models import ContactForm
from django.template import RequestContext
from django import forms
from django.forms.widgets import *
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from settings import EMAIL_HOST_USER

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



def contact(request):
    if request.method == 'POST':
       	form = ContactForm(request.POST)
       	if form.is_valid():
            cd = form.cleaned_data
			
            if cd['subject'] and cd['message'] and cd['email']:
                try:
                    send_mail(
                        cd['subject'],
			cd['email'] + '\n' + cd['message'],
			cd['email'],
			[EMAIL_HOST_USER],
			fail_silently=False,
                        )
                    url = reverse('contact_thank_you')
                    return HttpResponseRedirect(url)
                except BadHeaderError:
                    return HttpResponse('Invalid header found.')
            else:
                return HttpResponse('Make sure all fields are entered.')			
    else:
        form = ContactForm()
		
    return render_to_response('pages/contact.html', {'form':form}, RequestContext(request))

def thankyou(request):
    return render_to_response('pages/contact_thank_you.html')
