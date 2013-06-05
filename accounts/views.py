from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from accounts.models import NewUserForm, User, UserProfileForm, UserPhoneForm, UserVerificationForm
from django.core.urlresolvers import reverse
from windfriendly.models import NE
import twilio_utils
import random
import pytz
from django.utils.timezone import now
#from multi_choice import StringListField

def choose_new_id():
    userid = random.randint(10000000, 99999999)
    try:
        User.objects.get(pk=userid)
    except:
        return userid
    return choose_new_id()

def profile_create(request):
    # process submitted form
    if request.method == 'POST' and 'sign_up' in request.POST:
        form = NewUserForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            new_user = form.save(commit = False)
            new_user.verification_code = random.randint(100000, 999999)
            new_user.is_verified = False
            new_user.userid = choose_new_id()
            new_user.save()

            # redirect
            if new_user.is_valid_state():
                # to phone setup
                url = reverse('phone_setup', kwargs={'userid': new_user.userid})
                return HttpResponseRedirect(url)
            else:
                # to generic thanks
                url = reverse('thanks')
                return HttpResponseRedirect(url)
    else:
        form = NewUserForm() # An unbound form

    # Compute current greenery for NE
    datum = NE.objects.all().latest('date')
    percent_green = datum.fraction_green() * 100.0
    greenery = str(int(percent_green + 0.5)) + '%'

    # display form
    return render(request, 'index.html', {'form': form,
                                          'current_green' : greenery,
                                          'time': now()
                                          })

def phone_setup(request, userid):
    # process submitted phone number
    user = get_object_or_404(User, pk=userid)
    if request.method == 'POST':
        form = UserPhoneForm(request.POST, instance = user)
        if form.is_valid():# Check if the phone number entered is in the correct format
            form.save()
            verification_code = user.verification_code
            print ("Sending verification code: {:d}".format(verification_code))
            phonenumber = '+1'
            for c in user.phone:
                if c in '0123456789':
                    phonenumber += str(c)
            sent = twilio_utils.send_text(str(verification_code), phonenumber)
            print sent

            # Redirect to the code verification
            url = reverse('phone_verify', kwargs={'userid': userid})
            return HttpResponseRedirect(url)
    else:
        form = UserPhoneForm(instance = user) # An unbound form

    # display form
    return render(request, 'accounts/phone_setup.html', {
            'form': form,
            'userid': userid,
    })

def profile_alpha(request, userid):
    user = get_object_or_404(User, pk=userid)

    if not user.is_verified:
        url = reverse('phone_setup', kwargs={'userid': userid})
        return HttpResponseRedirect(url)

    # process submitted form
    if request.method == 'POST':
        form = UserProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            goals = form.cleaned_data.get('goal')
            print goals
            new_profile = form.save(commit=False)
            new_profile.userid = user
            new_profile.goal = ' '.join(each.encode('utf-8') for each in goals)
            new_profile.goal = new_profile.goal[0]
            #print type(new_profile.goal)
            #print type(new_profile.goal[0])
            new_profile.save()

            # redirect
            url = reverse('welcome_alpha')
            return HttpResponseRedirect(url)
    else:
        form = UserProfileForm() # An unbound form

    # display form
    return render(request, 'accounts/signup_alpha.html', {
            'form': form,
            'userid': userid,
    })

def phone_verify(request, userid):
    user = get_object_or_404(User,pk=userid)

    if user.is_verified:
        url = reverse('profile_alpha', kwargs={'userid':userid})
        return HttpResponseRedirect(url)

    if request.method == 'POST':
        form = UserVerificationForm(request.POST)
        if form.is_valid():
            code1 = form.cleaned_data['verification_code']
            code2 = user.verification_code
            print ("Checking codes: {:d} vs. {:d}".format(code1, code2))
            if code1 == code2:
                user.is_verified = True
                user.save()
                url = reverse('profile_alpha', kwargs={'userid':userid})
                return HttpResponseRedirect(url)
            else:
                # Meh
                url = reverse('phone_setup', kwargs={'userid': userid})
                return HttpResponseRedirect(url)
    else:
        form = UserVerificationForm()

    return render(request, 'accounts/phone_verify.html', {
        'form': form,
        'userid': userid,
    })

def thanks(request):
    return render(request, 'accounts/thanks_no_alpha.html')

def welcome_alpha(request):
    return render(request, 'accounts/thanks_alpha.html')
    

#@login_required
#def profile_edit(request):
#    success = False
#    user = User.objects.get(pk=request.user.id)
#    if request.method == 'POST':
#        upform = UserProfileForm(request.POST, instance=user.get_profile())
#        if upform.is_valid():
#            up = upform.save(commit=False)
#            up.user = request.user
#            up.save()
#            success = True
#    else:
#        upform = UserProfileForm(instance=user.get_profile())
#    return render_to_response('profile/index.html',
#        locals(), context_instance=RequestContext(request))
