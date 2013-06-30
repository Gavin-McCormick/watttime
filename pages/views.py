from django.shortcuts import render, render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from models import ContactForm
from django.template import RequestContext
from django import forms
from django.forms.widgets import *
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from windfriendly.models import NE, MARGINAL_FUELS
from windfriendly.parsers import NEParser
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

def BPA_status(request):
#    return render(request, 'pages/placeholder.html', {'title': 'Pacific Northwest current status'})
	
	 # compose message
    message = "Hi Anna! This is as far as I got. Couldn't figure out how to pull BPA data after all. :-/ Gavin"
    
    return render(request, 'pages/BPA_status.html', {'marginal_message' : message})
	
    return render(request, 'pages/BPA_status.html')
	
def CA_status(request):
#    return render(request, 'pages/placeholder.html', {'title': 'California current status'})
	
	 # compose message
    message = "Hi Anna! This is as far as I got. Couldn't figure out how to pull CAISO data after all. :-/ Gavin"
    
    return render(request, 'pages/CA_status.html', {'marginal_message' : message})
	
    return render(request, 'pages/CA_status.html')
	
def NE_status(request):
#    return render(request, 'pages/placeholder.html', {'title': 'New England current status'})
	# get current data
    if NE.objects.count() == 0:
        parser = NEParser()
        parser.update()

def status_offline(request):
    return render(request, 'pages/status.html', {'marginal_message' : 'Status is offline until July 1.'})

def status(request):
    datum = NE.objects.all().latest('date')
    percent_green = datum.fraction_green() * 100.0
    marginal_fuel = MARGINAL_FUELS[datum.marginal_fuel]
	
	 # compose message
    greenery = str(int(percent_green + 0.5))
    if marginal_fuel == 'None':
        marginal_fuel = 'Mixed'
    if marginal_fuel in ['Coal', 'Oil']:
        message = "Right now in New England {p} percent of all power is coming from renewable energy. You can change this number! Right now any new power that's needed will come from {fuel}. That means this is a great time to SAVE energy."
    elif marginal_fuel in ['Natural Gas', 'Refuse', 'Mixed']:
        message = "Right now in New England {p} percent of all power is coming from renewable energy. Right now any new power that's needed will come from {fuel}. That means this is an AVERAGE time to use energy."
    else:
        message = "Right now in New England {p} percent of all power is coming from renewable energy. You can change this number! Right now any new power that's needed will come from {fuel}. That means this is a fine time to use MORE power."
    message = message.format(p = greenery, fuel = marginal_fuel.lower())
    return render(request, 'pages/NE_status.html', {'marginal_message' : message})
	
    return render(request, 'pages/NE_status.html')
	
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
    
def facebook_pilot(request):
    return render(request, 'pages/facebook_pilot.html')
    
def sierra_pilot(request):
    return render(request, 'pages/sierra_pilot.html')
