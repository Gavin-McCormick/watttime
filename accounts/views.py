from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
# from accounts.models import NewUserForm, User, UserProfileForm, UserPhoneForm, UserVerificationForm
from accounts.models import UserProfile, PhoneVerificationForm, UserProfileForm, SignupForm, SENDTEXT_FREQ_SHORT, EQUIPMENT_SHORT, LoginForm, UserProfileFirstForm
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django_localflavor_us.us_states import STATE_CHOICES
from windfriendly.models import NE, CAISO
from windfriendly.parsers import NEParser, CAISOParser
import random
import pytz
from accounts import messages
from accounts.twilio_utils import send_text
from django.utils.timezone import now
from django.core.mail import send_mail
from django.http import HttpResponse, HttpResponseRedirect
from settings import EMAIL_HOST_USER
import accounts.twilio_utils
#from multi_choice import StringListField

def new_user_name():
    uid = str(random.randint(10000000, 99999999))
    try:
        User.objects.get(username=uid)
    except:
        return uid
    else:
        return new_user_name()

def new_phone_verification_number():
    return random.randint(100000, 999999)

def create_new_user(email):
    ups = UserProfile.objects.filter(email = email)
    if len(ups) > 0:
        print (len(ups))
        print ("User(s) with email {} already exists, aborting user creation!".
                format(email))
        return None


    username = new_user_name()
    user = User.objects.create_user(username, email = email, password = None)
    user.is_active = True
    user.is_staff = False
    user.is_superuser = False
    # The following fields are fields we store in the UserProfile object instead
    #   user.first_name
    #   user.last_name
    #   user.email
    user.save()

    up = UserProfile()
    up.user = user
    up.password_is_set = False
    up.magic_login_code = random.randint(100000000, 999999999)
    # If the user doesn't specify a name, email is used as the default
    up.name = email
    up.email = email
    up.phone = ''
    up.verification_code = new_phone_verification_number()
    up.is_verified = False
    up.state = 'CA'

    up.message_frequency = 1
    up.forecast_email = False
    up.set_equipment([])
    up.beta_test = False

    # In the future, we should separate phone-number, etc., into a separate model

    up.save()

    print ("User {} created.".format(email))
    return user

def create_and_email_user(email):
    user = create_new_user(email)
    if user:
        magic_url = "http://watttime.herokuapp.com/profile/{:d}".format(
                user.get_profile().magic_login_code)
        send_mail('Welcome to WattTime',
                messages.invite_message(email, magic_url),
                EMAIL_HOST_USER,
                [email])
        return True
    else:
        return False

def http_invite(request, email):
    if create_and_email_user(email):
        return HttpResponse("Sent email to {}".format(email), "application/json")
    else:
        return HttpResponse("User already exists", "application/json")

def email_login_user(user):
    magic_url = "http://watttime.herokuapp.com/profile/{:d}".format(
            user.get_profile().magic_login_code)
    send_mail('Account recovery for WattTime',
            messages.resend_login_message(user.get_profile().name, magic_url),
            EMAIL_HOST_USER,
            [user.get_profile().email])

def magic_login(request, magic_login_code):
    magic_login_code = int(magic_login_code)

    # Is there a user with that login code?
    try:
        up = UserProfile.objects.get(magic_login_code = magic_login_code)
    except:
        # No such user.
        print ("No user with login code {}".format(magic_login_code))
        url = reverse('accounts.views.frontpage')
        return HttpResponseRedirect(url)
    else:
        # This is necessary because one cannot login without authenticating
        up.password_is_set = False
        user = up.user
        pw = str(random.randint(1000000000, 9999999999))
        user.set_password(pw)
        user.save()

        # 'authenticate' attaches a 'backend' object to the returned user,
        # which is necessary for the login process
        user = authenticate(username = user.username, password = pw)

        login(request, user)
        print ("Logged in user {}".format(up.name))
        url = reverse('profile_first_edit')
        return HttpResponseRedirect(url)

# Returns True if code sent successfully, otherwise False
def send_verification_code(user):
    up = user.get_profile()
    code = new_phone_verification_number()
    up.verification_code = code
    up.save()
    print ("Sending {} verification code {:d}".format(up.name, code))
    msg = messages.verify_phone_message(code)
    sent = accounts.twilio_utils.send_text(msg, up)
    if sent:
        print ("Send successful.")
    else:
        print ("Send unsuccessful.")
    return sent

def profile_edit(request):
    user = request.user
    if user.is_authenticated():
        up = user.get_profile()

        if request.method == 'POST':
            form = UserProfileForm(request.POST)
            if form.is_valid():
                # User posted changes to profile

                name = form.cleaned_data['name']
                if name and len(name) < 100 and name != up.name:
                    print ("Changing name")
                    up.name = name

                password = form.cleaned_data['password']
                if password == '' and up.password_is_set:
                    print ("Removing password")
                    up.password_is_set = False
                elif not (password == '(not used)') and (not password == '######'):
                    print ("Setting password")
                    up.user.set_password(password)
                    up.user.save()
                    up.password_is_set = True

                phone = form.cleaned_data['phone']
                if phone and (phone != up.phone):
                    print ("Changing phone")
                    up.phone = phone
                    up.is_verified = False

                freq = int(form.cleaned_data['message_frequency'])
                if freq != up.message_frequency:
                    print ("Changing message frequency")
                    up.message_frequency = freq

                fe = form.cleaned_data['forecast_email']
                if fe != up.forecast_email:
                    print ("Changing forecast email")
                    up.forecast_email = fe

                eq = list(int(i) for i in (form.cleaned_data['equipment']))
                if eq != up.get_equipment():
                    print ("Changing equipment")
                    up.set_equipment(eq)

                beta_test = form.cleaned_data['beta_test']
                if beta_test != up.beta_test:
                    print ("Changing beta test")
                    up.beta_test = beta_test

                up.save()

                print ("Saved profile information")

                url = reverse('profile_view')
                return HttpResponseRedirect(url)
        else:
            if up.password_is_set:
                password = '######'
            else:
                password = '(not used)'

            form = UserProfileForm(initial =
                    {'name' : up.name,
                    'password' : password,
                    'phone' : up.phone,
                    'message_frequency' : up.message_frequency,
                    'forecast_email' : up.forecast_email,
                    'equipment' : up.get_equipment(),
                    'beta_test' : up.beta_test})
            # User is viewing profile information
            print ("Display profile information")

        vals = {
                'name' : up.name,
                'email' : up.email,
                'state' : up.state,
                'form' : form,
                }

        return render(request, 'accounts/profile_edit.html', vals)
    else:
        print ("User not authenticated")
        url = reverse('user_login')
        return HttpResponseRedirect(url)

def profile_first_edit(request):
    user = request.user
    if user.is_authenticated():
        up = user.get_profile()

        if request.method == 'POST':
            form = UserProfileFirstForm(request.POST)
            if form.is_valid():
                # User posted changes to profile

                password = form.cleaned_data['password']
                if password == '' and up.password_is_set:
                    print ("Removing password")
                    up.password_is_set = False
                elif not (password == '(not used)') and (not password == '######'):
                    print ("Setting password")
                    up.user.set_password(password)
                    up.user.save()
                    up.password_is_set = True

                phone = form.cleaned_data['phone']
                if phone and (phone != up.phone):
                    print ("Changing phone")
                    up.phone = phone
                    up.is_verified = False

                up.save()

                print ("Saved profile information")

                url = reverse('phone_verify_view')
                return HttpResponseRedirect(url)
        else:
            initial = {}
            if up.phone:
                initial['phone'] = up.phone

            form = UserProfileFirstForm()
            # User is viewing profile information
            print ("Display profile information")

        vals = {
                'name' : up.name,
                'form' : form,
                }

        return render(request, 'accounts/profile_first_edit.html', vals)
    else:
        print ("User not authenticated")
        url = reverse('user_login')
        return HttpResponseRedirect(url)

def profile_view(request):
    user = request.user
    if user.is_authenticated():
        up = user.get_profile()

        if up.phone:
            if up.is_verified:
                phone = up.phone + ' (verified)'
            else:
                phone = up.phone + ' (not verified)'
        else:
            phone = '(none)'

        freq = SENDTEXT_FREQ_SHORT[up.message_frequency]

        if up.forecast_email:
            morning_forecast = 'Yes'
        else:
            morning_forecast = 'No'

        equipment = up.get_equipment()
        if equipment:
            equipment = '; '.join(EQUIPMENT_SHORT[i] for i in equipment)
        else:
            equipment = '(none)'

        if up.beta_test:
            beta_test = 'Yes'
        else:
            beta_test = 'No'

        vals = {
                'name' : up.name,
                'email' : up.email,
                'state' : up.state,
                'phone_number' : phone,
                'message_frequency' : freq,
                'morning_forecast' : morning_forecast,
                'equipment' : equipment,
                'beta_test' : beta_test,
                'phone_verified' : up.is_verified,
                'phone_blank' : (len(up.phone) == 0),
                'deactivated' : (not user.is_active)
                }

        return render(request, 'accounts/profile.html', vals)
    else:
        print ("User not authenticated")
        url = reverse('user_login')
        return HttpResponseRedirect(url)

def phone_verify_view(request):
    user = request.user

    if user.is_authenticated():
        up = user.get_profile()
        phone = up.phone

        if up.is_verified:
            # Phone already verified
            print ("Already verified")
            return render(request, 'accounts/phone_already_verified.html',
                    {'phone_number' : phone})

        elif request.method == 'POST':
            # User posts a verification code, we confirm or not
            code = int(request.POST['verification_code'])
            print ("Comparing verification codes {:d} (true) vs {:d} (claimed)".
                    format(up.verification_code, code))
            if code == up.verification_code:
                up.is_verified = True
                up.save()
                # Success
                print ("Success")
                url = reverse('profile_view')
                return HttpResponseRedirect(url)
            else:
                # Failure
                print ("Failure")
                form = PhoneVerificationForm()
                return render(request, 'accounts/phone_verification_wrong.html',
                        {'phone_number' : phone, 'form' : form})
        else:
            # Send a verification code
            # TODO first check if phone number hasn't been set yet.
            sent = send_verification_code(user)
            if sent:
                form = PhoneVerificationForm()
                print ("Sent verification code")
                return render(request, 'accounts/phone_verify.html',
                        {'phone_number' : phone, 'form' : form})
            else:
                print ("Unable to send verification code to phone number")
                return render(request, 'accounts/phone_bad_number.html',
                        {'phone_number' : phone})
    else:
        print ("User not authenticated")
        url = reverse('user_login')
        return HttpResponseRedirect(url)

def user_login(request):
    if request.user.is_authenticated():
        url = reverse('profile_view')
        return HttpResponseRedirect(url)
    elif request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            try:
                up = UserProfile.objects.get(email = email)
            except:
                return render(request, 'accounts/no_such_user.html', {'email' : email})
            else:
                if password:
                    user = authenticate(username = up.user.username, password = password)
                    if user and up.password_is_set:
                        login(request, user)
                        url = reverse('profile_view')
                        return HttpResponseRedirect(url)
                    else:
                        return render(request, 'accounts/wrong_password.html', {'email' : email})
                else:
                    email_login_user(up.user)
                    url = reverse('accounts.views.frontpage')
                    return HttpResponseRedirect(url)
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form' : form})

def create_user(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            create_and_email_user(form.cleaned_data['email'])
            url = reverse('signed_up')
            return HttpResponseRedirect(url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form' : form})

def frontpage(request):
    if CAISO.objects.count() == 0:
        parser = CAISOParser()
        parser.update()
    datum = CAISO.latest_point()
    percent_green = datum.fraction_green() * 100.0
    greenery = str(int(percent_green + 0.5)) + '%'

    form = SignupForm()
    return render(request, 'index.html',
            {'form' : form, 'current_green' : greenery})

def deactivate(request):
    user = request.user
    if user.is_authenticated():
        print ("Deactivating!")
        user.is_active = False
        user.save()
        url = reverse('accounts.views.frontpage')
        return HttpResponseRedirect(url)
    else:
        url = reverse('user_login')
        return HttpResponseRedirect(url)

def reactivate(request):
    user = request.user
    if user.is_authenticated():
        print ("Reactivating!")
        user.is_active = True
        user.save()
        url = reverse('profile_view')
        return HttpResponseRedirect(url)
    else:
        url = reverse('user_login')
        return HttpResponseRedirect(url)

### Old stuff

def choose_new_id():
    userid = random.randint(10000000, 99999999)
    try:
        User.objects.get(pk=userid)
    except:
        return userid
    return choose_new_id()

def shut_down(request):
    return render(request, 'shut_down.html')

def profile_create(request):
    last_url = request.get_full_path()[-8:]
    print (dir(request))
    print (type(request.session))
    print (repr(request.session))
    print (dir(request.session))
    # if request.user and request.user.is_authenticated():
        # print ("Saving!", request.user.email)
        # request.user.save()
    # print (request.user.is_authenticated())
    # print (request.user.is_active)
    # print (request.user.id)
    # print (request.user.__class__)
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
                      messages.email_signup_message(new_user.userid, new_user.name).msg,
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
    if NE.objects.count() == 0:
        parser = NEParser()
        parser.update()
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
                          messages.account_activated_message(user.userid,
                                                    user.name,
                                                    user.phone).msg,
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
                          messages.account_activated_message(user.userid,
                                                    user.name,
                                                    user.phone).msg,
                          EMAIL_HOST_USER,
                          [user.email],
                          fail_silently=False)

                # send text
                msg = messages.intro_message()
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
                              messages.account_inactivated_message(user.userid,
                                                                  user.name,
                                                                  user.phone).msg,
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
