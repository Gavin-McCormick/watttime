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
from accounts.messages import verify_phone_message, email_signup_message, account_activated_message, account_inactivated_message, intro_message
from accounts.twilio_utils import send_text
from django.utils.timezone import now
from django.core.mail import send_mail
from settings import EMAIL_HOST_USER
#from multi_choice import StringListField

def choose_new_id():
    userid = random.randint(10000000, 99999999)
    try:
        User.objects.get(pk=userid)
    except:
        return userid
    return choose_new_id()

def profile_create(request):
    last_url = request.get_full_path()[-8:]
    print last_url
    # process submitted form
    if request.method == 'POST' and 'sign_up' in request.POST:
        form = NewUserForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            new_user = form.save(commit = False)
            new_user.verification_code = random.randint(100000, 999999)
            new_user.is_verified = False
            new_user.is_active = False
            new_user.userid = choose_new_id()
            new_user.save()

            # send email
            send_mail('Welcome to WattTime',
                      email_signup_message(new_user.userid, new_user.name),
                      EMAIL_HOST_USER,
                      [new_user.email],
                      fail_silently=False)

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
    if last_url == 'profile/':
        return render(request, 'account/profile.html', {'form': form})
    else:
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
            send_verification_code(user)

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
            new_profile = form.save(commit=False)
            new_profile.userid = user
            new_profile.goal = ' '.join(each.encode('utf-8') for each in goals)
            new_profile.goal = new_profile.goal[0]
            #print type(new_profile.goal)
            #print type(new_profile.goal[0])
            new_profile.save()

            # send text
            msg = new_profile.get_edit_profile_message()
            send_text(msg, to=user.phone)

            # reactivate user
            if not user.is_active:
                user.is_active = True
                user.save()

                # send email
                send_mail('WattTime account activated',
                          account_activated_message(user.userid,
                                                    user.name,
                                                    user.phone),
                          EMAIL_HOST_USER,
                          [user.email],
                          fail_silently=False)

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

def send_verification_code(user):
    verification_code = user.verification_code
    print ("Sending verification code: {:d}".format(verification_code))
    phonenumber = '+1'
    for c in user.phone:
        if c in '0123456789':
            phonenumber += str(c)
    msg = verify_phone_message(verification_code)
    sent = twilio_utils.send_text(msg, phonenumber)
    print sent

def phone_verify(request, userid):
    user = get_object_or_404(User,pk=userid)
    print request.get_full_path()[-6:]
    if "resend" == request.get_full_path()[-6:]:
        print "resending message..."
        send_verification_code(user)
        form = UserVerificationForm()
        return render(request, 'accounts/phone_verify.html', {
    		'form': form,
    		'userid': userid,
    		'reenter': False,
    		'resend' : True,
    		'phone' : user.phone,
        })

    # Note: code after this won't get called until event triggers (this is like a listener)
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
                # save verification and activation state
                user.is_verified = True
                user.is_active = True
                user.save()

                # send email
                send_mail('WattTime account activated',
                          account_activated_message(user.userid,
                                                    user.name,
                                                    user.phone),
                          EMAIL_HOST_USER,
                          [user.email],
                          fail_silently=False)

                # send text
                msg = intro_message()
                send_text(msg, to=user.phone)

                # redirect
                url = reverse('profile_alpha', kwargs={'userid':userid})
                return HttpResponseRedirect(url)
            else:
                # Meh
                #url = reverse('phone_verify', kwargs={'userid': userid, 'reenter' :True})
                return render(request, 'accounts/phone_verify.html', {'form': form, 'userid' : userid, 'reenter' : True, 'resend' : False, 'phone' : user.phone})
                #url = reverse('phone_setup', kwargs={'userid': userid})
                #return HttpResponseRedirect(url)
    else:
        form = UserVerificationForm()

    return render(request, 'accounts/phone_verify.html', {
        'form': form,
        'userid': userid,
        'reenter': False,
        'resend' : False,
        'phone' : user.phone,
    })

def thanks(request):
    return render(request, 'accounts/thanks_no_alpha.html')

def welcome_alpha(request):
    return render(request, 'accounts/thanks_alpha.html')

def unsubscribe(request, phone):
    """ Set user(s) with matching phone number to verified but inactive """
    if phone:
        phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
        users = User.objects.filter(phone=phone)
        print users
        if len(users) > 0:
            show_name, show_id = None, None
            for user in users:
                # inactivate
                if user.is_active:
                    # log
                    print user
                    show_name = user.name
                    show_id = user.userid

                    # save inactivation
                    user.is_active = False
                    user.save()

                    # send email
                    send_mail('WattTime account inactivated',
                              account_inactivated_message(user.userid,
                                                          user.name,
                                                          user.phone),
                              EMAIL_HOST_USER,
                              [user.email],
                              fail_silently=False)

            if show_name:
                return render(request, 'accounts/unsubscribe_success.html', {
                        'phone': phone,
                        'name': show_name,
                        'userid': show_id,
                        })
            else:
                return render(request, 'accounts/unsubscribe_fail.html', {
                        'phone': phone,
                        })
        else:
            return render(request, 'accounts/unsubscribe_fail.html', {
                    'phone': phone,
                    })
    else:
        return render(request, 'accounts/unsubscribe_fail.html', {
                'phone': phone,
                })

def user_profile(request):
	pass
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
