from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.core.mail import send_mail, BadHeaderError
from django.core.urlresolvers import reverse
from settings import EMAIL_HOST_USER

from models import ContactForm
from accounts.forms import SignupForm
from windfriendly.balancing_authorities import BA_MODELS, BA_PARSERS, BALANCING_AUTHORITIES

def server_error(request):
    return render(request, 'pages/500.html')

def notfound_error(request):
    return render(request, 'pages/404.html')

def frontpage(request):
    # set state
    # TODO get from user location
    state = 'CA'
    
    # get ba for state
    ba_name = BALANCING_AUTHORITIES[state]
    ba = BA_MODELS[ba_name]
    ba_parser = BA_PARSERS[ba_name]
    
    # get current percent green
    if ba.objects.count() == 0:
        parser = ba_parser()
        parser.update()
    datum = ba.objects.all().filter(forecast_code=0).latest()
    percent_green = datum.fraction_clean * 100.0
    greenery = str(round(percent_green, 1)) + '%'

    # set up signup form
    form = SignupForm(initial = {'state' : u'%s' % state})
    
    # return
    return render(request, 'index.html',
            {'signup_form' : form, 'current_green' : greenery})

def status(request):
    user = request.user

    try:
        user_agent = request.META['HTTP_USER_AGENT']
        print ("User agent: {}".format(user_agent))
        is_internet_explorer = ('MSIE' in user_agent)
    except KeyError:
        is_internet_explorer = False

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
