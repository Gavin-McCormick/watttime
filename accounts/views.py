from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from accounts import models, forms, messages, twilio_utils, regions
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate
from django.core.urlresolvers import reverse
from django_localflavor_us.us_states import STATE_CHOICES
from windfriendly.models import CAISO
from windfriendly.parsers import CAISOParser
import random
from django.utils.timezone import now
from django.core.mail import send_mail
import settings

def redirect(url):
    return HttpResponseRedirect(reverse(url))

class FormView:
    def __init__(self, html_file, form):
        self.require_authentication = True
        self.html_file = html_file
        self._form = form

    def form(self, user):
        return self._form

    def form_initial(self, user):
        return {}

    def html_params(self, user):
        return {}

    def form_submitted(self, request, vals):
        raise NotImplementedError()

    def render(self, request, html, vals):
        return render(request, html, vals)

    def __call__(self, request):
        user = request.user
        if (not self.require_authentication) or user.is_authenticated():
            if request.method == 'POST':
                form = self.form(user)(request.POST)
                if form.is_valid():
                    return self.form_submitted(request, form.cleaned_data)
            else:
                form = self.form(user)(initial = self.form_initial(user))

            vals = self.html_params(user)
            vals['form'] = form

            return self.render(request, 'accounts/{}.html'.format(self.html_file), vals)
        else:
            return redirect('user_login')

class ProfileEdit(FormView):
    def __init__(self):
        FormView.__init__(self, 'profile_edit', forms.UserProfileForm)

    def form(self, user):
        return user.get_profile().region().user_prefs_form

    def form_initial(self, user):
        up = user.get_profile()
        if up.password_is_set:
            password = '######'
        else:
            password = '(not used)'

        vals = {'name'              : up.name,
                'password'          : password,
                'state'             : up.state,
                'phone'             : up.phone,
                'equipment'         : up.get_equipment(),
                'beta_test'         : up.beta_test,
                'ask_feedback'      : up.ask_feedback}

        up.form_initial_values(vals)

        return vals

    def html_params(self, user):
        up = user.get_profile()
        return {'name' : up.name,
                'email' : up.email,
                'state' : up.state,
                'region' : up.region().name}

    def form_submitted(self, request, vals):
        up = request.user.get_profile()
        up.name = vals['name']

        password = vals['password']
        if not password in ['(not used)', '######']:
            up.set_password(password)

        up.set_phone(vals['phone'])
        up.set_equipment(list(int(i) for i in vals['equipment']))
        up.beta_test = vals['beta_test']
        up.ask_feedback = vals['ask_feedback']
        up.save_from_form(vals)

        # This MUST go after save_from_form because the UserProfile object
        # uses the value of the state variable to decide where to put the
        # region-specific settings, and any region-specific settings in the form
        # would pertain to the /old/ value of the state.
        up.state = vals['state']
        up.save()

        return redirect('profile_view')

class ProfileFirstEdit(FormView):
    def __init__(self):
        FormView.__init__(self, 'profile_first_edit', forms.UserProfileFirstForm)

    def form_initial(self, user):
        up = user.get_profile()
        return {'phone' : up.phone, 'state' : up.state}

    def html_params(self, user):
        up = user.get_profile()
        return {'name' : up.name, 'region_supported' : up.supported_location()}

    def form_submitted(self, request, vals):
        up = request.user.get_profile()

        password = vals['password']
        if not password in ['(not used)', '######']:
            up.set_password(password)

        up.set_phone(vals['phone'])
        up.state = vals['state']
        up.save()

        return redirect('phone_verify_view')

# A bit hackish
class PhoneVerifyView(FormView):
    def __init__(self):
        FormView.__init__(self, '', forms.PhoneVerificationForm)

    def form_submitted(self, request, vals):
        up = request.user.get_profile()
        code = int(vals['verification_code'])
        if code == up.verification_code:
            up.is_verified = True
            up.save()
            return redirect('profile_view')
        else:
            return render(request, 'accounts/phone_verification_wrong.html',
                    {'phone_number' : up.phone, 'form' : self.form()})

    def render(self, request, html, vals):
        user = request.user
        up = user.get_profile()
        vals['phone_number'] = up.phone
        if up.is_verified:
            return render(request, 'accounts/phone_already_verified.html', vals)
        else:
            # TODO specialized error message for blank phone number
            sent = send_verification_code(user)
            if sent:
                return render(request, 'accounts/phone_verify.html', vals)
            else:
                return render(request, 'accounts/phone_bad_number.html', vals)

class LoginView(FormView):
    def __init__(self):
        FormView.__init__(self, 'login', forms.LoginForm)
        self.require_authentication = False

    def form_submitted(self, request, vals):
        email       = vals['email']
        password    = vals['password']
        try:
            up = models.UserProfile.objects.get(email = email)
        except:
            return render(request, 'accounts/no_such_user.html', {'email' : email})
        else:
            if password:
                user = authenticate(username = up.user.username, password = password)
                if user and up.password_is_set:
                    login(request, user)
                    return redirect('profile_view')
                else:
                    return render(request, 'accounts/wrong_password.html', {'email' : email})
            else:
                email_login_user(up.user)
                return redirect('accounts.views.frontpage')

    def __call__(self, request):
        if request.user.is_authenticated():
            return redirect('profile_view')
        else:
            return FormView.__call__(self, request)

class CreateUserView(FormView):
    def __init__(self):
        FormView.__init__(self, 'signup', forms.SignupForm)
        self.require_authentication = False

    def form_submitted(self, request, vals):
        user = create_and_email_user(vals['email'], state = vals['state'])
        if user:
            if user.get_profile().supported_location():
                return redirect('signed_up')
            else:
                return redirect('signed_up_future')
        else:
            return render(request, 'accounts/user_already_exists.html',
                    {'email' : vals['email']})

profile_edit = ProfileEdit()

profile_first_edit = ProfileFirstEdit()

phone_verify_view = PhoneVerifyView()

user_login = LoginView()

create_user = CreateUserView()

def new_user_name():
    users = [None]
    while len(users) > 0:
        uid = str(random.randint(10000000, 99999999))
        users = User.objects.filter(username = uid)

    return uid

def new_phone_verification_number():
    return random.randint(100000, 999999)

def create_new_user(email, name = None, state = None):
    ups = models.UserProfile.objects.filter(email = email)
    if len(ups) > 0:
        print (len(ups))
        print ("User(s) with email {} already exists, aborting user creation!".
                format(email))
        return None

    username = new_user_name()
    user = User.objects.create_user(username, email = None, password = None)
    user.is_active = False
    user.is_staff = False
    user.is_superuser = False
    # The following fields are fields we store in the UserProfile object instead
    #   user.first_name
    #   user.last_name
    #   user.email
    user.save()

    up = models.UserProfile()
    up.user = user
    up.password_is_set = False
    up.magic_login_code = random.randint(100000000, 999999999)
    # If the user doesn't specify a name, email is used as the default
    if name is None:
        up.name = email
    else:
        up.name = name
    up.email = email
    up.phone = ''
    up.verification_code = new_phone_verification_number()
    up.is_verified = False

    if state is None:
        up.state = 'CA'
    else:
        up.state = state

    up.ca_settings = None
    up.ne_settings = None
    up.null_settings = None

    up.get_region_settings() # so that the region settings are not None

    up.set_equipment([])
    up.beta_test = True
    up.ask_feedback = False

    # In the future, we should separate phone-number, etc., into a separate model

    up.save()

    print ("User {} created.".format(email))
    return user

def create_and_email_user(email, name = None, state = None):
    user = create_new_user(email, name, state)
    if user:
        up = user.get_profile()
        magic_url = "http://watttime.herokuapp.com/profile/{:d}".format(
                up.magic_login_code)
        if up.supported_location():
            msg = messages.invite_message(email, magic_url, name)
        else:
            msg = messages.invite_message_unsupported(email, magic_url, name)

        send_mail('Welcome to WattTime',
                msg,
                settings.EMAIL_HOST_USER,
                [email])
        return user
    else:
        return None

def http_invite(request, email):
    if create_and_email_user(email):
        return HttpResponse("Sent email to {}".format(email), "application/json")
    else:
        return HttpResponse("User already exists", "application/json")

def http_invite_with_name(request, email, name):
    if create_and_email_user(email, name):
        return HttpResponse("Sent email to {} ({})".format(name, email), "application/json")
    else:
        return HttpResponse("User already exists", "application/json")

def email_login_user(user):
    magic_url = "http://watttime.herokuapp.com/profile/{:d}".format(
            user.get_profile().magic_login_code)
    send_mail('Account recovery for WattTime',
            messages.resend_login_message(user.get_profile().name, magic_url),
            settings.EMAIL_HOST_USER,
            [user.get_profile().email])

def magic_login(request, magic_login_code):
    magic_login_code = int(magic_login_code)

    # Is there a user with that login code?
    try:
        up = models.UserProfile.objects.get(magic_login_code = magic_login_code)
    except:
        # No such user.
        print ("No user with login code {}".format(magic_login_code))
        return redirect('accounts.views.frontpage')
    else:
        # This is necessary because one cannot login without authenticating
        up.password_is_set = False
        user = up.user
        pw = str(random.randint(1000000000, 9999999999))
        user.set_password(pw)
        user.is_active = True
        user.save()

        # 'authenticate' attaches a 'backend' object to the returned user,
        # which is necessary for the login process
        user = authenticate(username = user.username, password = pw)

        login(request, user)
        print ("Logged in user {}".format(up.name))
        return redirect('profile_first_edit')

# Returns True if code sent successfully, otherwise False
def send_verification_code(user):
    up = user.get_profile()
    code = new_phone_verification_number()
    up.verification_code = code
    up.save()
    print ("Sending {} verification code {:d}".format(up.name, code))
    msg = messages.verify_phone_message(code)
    sent = twilio_utils.send_text(msg, up, force = True)
    if sent:
        print ("Send successful.")
    else:
        print ("Send unsuccessful.")
    return sent

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

        equipment = up.get_equipment()
        if equipment:
            equipment = '; '.join(forms.EQUIPMENT_SHORT[i] for i in equipment)
        else:
            equipment = '(none)'

        if up.beta_test:
            beta_test = 'Yes'
        else:
            beta_test = 'No'

        if up.ask_feedback:
            ask_feedback = 'Yes'
        else:
            ask_feedback = 'No'

        vals = {
                'name' : up.name,
                'email' : up.email,
                'state' : up.state,
                'long_state' : up.long_state_name(),
                'region' : up.region().name,
                'phone_number' : phone,
                'equipment' : equipment,
                'beta_test' : beta_test,
                'ask_feedback' : ask_feedback,
                'supported_region' : up.supported_location(),
                'phone_verified' : up.is_verified,
                'phone_blank' : (len(up.phone) == 0),
                'deactivated' : (not user.is_active)
                }

        up.display_values(vals)

        return render(request, 'accounts/profile.html', vals)
    else:
        print ("User not authenticated")
        return redirect('user_login')

def frontpage(request):
    if CAISO.objects.count() == 0:
        parser = CAISOParser()
        parser.update()
    datum = CAISO.latest_point()
    percent_green = datum.fraction_green() * 100.0
    greenery = str(int(percent_green + 0.5)) + '%'

    form = forms.SignupForm(initial = {'state' : u'CA'})
    return render(request, 'index.html',
            {'form' : form, 'current_green' : greenery})

def set_active(request, new_value):
    user = request.user
    if user.is_authenticated():
        user.is_active = new_value
        user.save()
        return redirect('profile_view')
    else:
        return redirect('user_login')

def deactivate(request):
    return set_active(request, False)

def reactivate(request):
    return set_active(request, True)




def old_profile_edit(request):
    user = request.user
    prev_state = user.state
    if user.is_authenticated():
        up = user.get_profile()

        if request.method == 'POST':
            form = forms.UserProfileForm(request.POST)
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

                state = form.cleaned_data['state']
                if state and (state != up.state):
                    print ("Changing state")
                    up.state = state

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

            form = forms.UserProfileForm(initial =
                    {'name' : up.name,
                    'password' : password,
                    'state' : up.state,
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

def old_profile_first_edit(request):
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
                    up.user.set_unusable_password()
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

                state = form.cleaned_data['state']
                if state and (state != up.state):
                    print ("Changing state")
                    up.state = state

                up.save()

                print ("Saved profile information")

                url = reverse('phone_verify_view')
                return HttpResponseRedirect(url)
        else:
            initial = {}
            if up.phone:
                initial['phone'] = up.phone
            initial['state'] = up.state

            form = UserProfileFirstForm(initial = initial)
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
def old_phone_verify_view(request):
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

def old_user_login(request):
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

def old_create_user(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            user = create_and_email_user(form.cleaned_data['email'])
            up = user.get_profile()
            up.state = form.cleaned_data['state']
            up.save()

            url = reverse('signed_up')
            return HttpResponseRedirect(url)
    else:
        form = SignupForm()
    return render(request, 'accounts/signup.html', {'form' : form})

### Old stuff
# 
# def choose_new_id():
#     userid = random.randint(10000000, 99999999)
#     try:
#         User.objects.get(pk=userid)
#     except:
#         return userid
#     return choose_new_id()
# 
# def shut_down(request):
#     return render(request, 'shut_down.html')
# 
# def profile_create(request):
#     last_url = request.get_full_path()[-8:]
#     print (dir(request))
#     print (type(request.session))
#     print (repr(request.session))
#     print (dir(request.session))
#     # if request.user and request.user.is_authenticated():
#         # print ("Saving!", request.user.email)
#         # request.user.save()
#     # print (request.user.is_authenticated())
#     # print (request.user.is_active)
#     # print (request.user.id)
#     # print (request.user.__class__)
#     print last_url
#     # process submitted form
#     if request.method == 'POST' and 'sign_up' in request.POST:
#         form = NewUserForm(request.POST) # A form bound to the POST data
#         if form.is_valid(): # All validation rules pass
#             # save form
#             new_user = form.save(commit = False)
#             new_user.verification_code = random.randint(100000, 999999)
#             new_user.is_verified = False
#             new_user.is_active = False
#             new_user.userid = choose_new_id()
#             new_user.save()
# 
#             # send email
#             send_mail('Welcome to WattTime',
#                       messages.email_signup_message(new_user.userid, new_user.name).msg,
#                       EMAIL_HOST_USER,
#                       [new_user.email],
#                       fail_silently=False)
# 
#             # redirect
#             if new_user.is_valid_state():
#                 # to phone setup
#                 url = reverse('phone_setup', kwargs={'userid': new_user.userid})
#                 return HttpResponseRedirect(url)
#             else:
#                 # to generic thanks
#                 url = reverse('thanks')
#                 return HttpResponseRedirect(url)
#     else:
#         form = NewUserForm() # An unbound form
# 
#     # Compute current greenery for NE
#     if NE.objects.count() == 0:
#         parser = NEParser()
#         parser.update()
#     datum = NE.objects.all().latest('date')
#     percent_green = datum.fraction_green() * 100.0
#     greenery = str(int(percent_green + 0.5)) + '%'
# 
#     # display form
#     if last_url == 'profile/':
#         return render(request, 'account/profile.html', {'form': form})
#     else:
#         return render(request, 'index.html', {'form': form,
#                                               'current_green' : greenery,
#                                               'time': now()
#                                               })
# 
# def phone_setup(request, userid):
#     # process submitted phone number
#     user = get_object_or_404(User, pk=userid)
#     if request.method == 'POST':
#         form = UserPhoneForm(request.POST, instance = user)
#         if form.is_valid():# Check if the phone number entered is in the correct format
#             form.save()
#             send_verification_code(user)
# 
#             # Redirect to the code verification
#             url = reverse('phone_verify', kwargs={'userid': userid})
#             return HttpResponseRedirect(url)
#     else:
#         form = UserPhoneForm(instance = user) # An unbound form
# 
#     # display form
#     return render(request, 'accounts/phone_setup.html', {
#             'form': form,
#             'userid': userid,
#     })
# 
# def profile_alpha(request, userid):
#     user = get_object_or_404(User, pk=userid)
# 
#     if not user.is_verified:
#         url = reverse('phone_setup', kwargs={'userid': userid})
#         return HttpResponseRedirect(url)
# 
#     # process submitted form
#     if request.method == 'POST':
#         form = UserProfileForm(request.POST) # A form bound to the POST data
#         if form.is_valid(): # All validation rules pass
#             # save form
#             goals = form.cleaned_data.get('goal')
#             new_profile = form.save(commit=False)
#             new_profile.userid = user
#             new_profile.goal = ' '.join(each.encode('utf-8') for each in goals)
#             new_profile.goal = new_profile.goal[0]
#             #print type(new_profile.goal)
#             #print type(new_profile.goal[0])
#             new_profile.save()
# 
#             # send text
#             msg = new_profile.get_edit_profile_message()
#             send_text(msg, to=user.phone)
# 
#             # reactivate user
#             if not user.is_active:
#                 user.is_active = True
#                 user.save()
# 
#                 # send email
#                 send_mail('WattTime account activated',
#                           messages.account_activated_message(user.userid,
#                                                     user.name,
#                                                     user.phone).msg,
#                           EMAIL_HOST_USER,
#                           [user.email],
#                           fail_silently=False)
# 
#             # redirect
#             url = reverse('welcome_alpha')
#             return HttpResponseRedirect(url)
#     else:
#         form = UserProfileForm() # An unbound form
# 
#     # display form
#     return render(request, 'accounts/signup_alpha.html', {
#             'form': form,
#             'userid': userid,
#     })
# 
# def phone_verify(request, userid):
#     user = get_object_or_404(User,pk=userid)
#     print request.get_full_path()[-6:]
#     if "resend" == request.get_full_path()[-6:]:
#         print "resending message..."
#         send_verification_code(user)
#         form = UserVerificationForm()
#         return render(request, 'accounts/phone_verify.html', {
#     		'form': form,
#     		'userid': userid,
#     		'reenter': False,
#     		'resend' : True,
#     		'phone' : user.phone,
#         })
# 
#     # Note: code after this won't get called until event triggers (this is like a listener)
#     if user.is_verified:
#         url = reverse('profile_alpha', kwargs={'userid':userid})
#         return HttpResponseRedirect(url)
# 
#     if request.method == 'POST':
#         form = UserVerificationForm(request.POST)
#         if form.is_valid():
#             code1 = form.cleaned_data['verification_code']
#             code2 = user.verification_code
#             print ("Checking codes: {:d} vs. {:d}".format(code1, code2))
# 
#             if code1 == code2:
#                 # save verification and activation state
#                 user.is_verified = True
#                 user.is_active = True
#                 user.save()
# 
#                 # send email
#                 send_mail('WattTime account activated',
#                           messages.account_activated_message(user.userid,
#                                                     user.name,
#                                                     user.phone).msg,
#                           EMAIL_HOST_USER,
#                           [user.email],
#                           fail_silently=False)
# 
#                 # send text
#                 msg = messages.intro_message()
#                 send_text(msg, to=user.phone)
# 
#                 # redirect
#                 url = reverse('profile_alpha', kwargs={'userid':userid})
#                 return HttpResponseRedirect(url)
#             else:
#                 # Meh
#                 #url = reverse('phone_verify', kwargs={'userid': userid, 'reenter' :True})
#                 return render(request, 'accounts/phone_verify.html', {'form': form, 'userid' : userid, 'reenter' : True, 'resend' : False, 'phone' : user.phone})
#                 #url = reverse('phone_setup', kwargs={'userid': userid})
#                 #return HttpResponseRedirect(url)
#     else:
#         form = UserVerificationForm()
# 
#     return render(request, 'accounts/phone_verify.html', {
#         'form': form,
#         'userid': userid,
#         'reenter': False,
#         'resend' : False,
#         'phone' : user.phone,
#     })
# 
# def thanks(request):
#     return render(request, 'accounts/thanks_no_alpha.html')
# 
# def welcome_alpha(request):
#     return render(request, 'accounts/thanks_alpha.html')
# 
# def unsubscribe(request, phone):
#     """ Set user(s) with matching phone number to verified but inactive """
#     if phone:
#         phone = phone[0:3]+'-'+phone[3:6]+'-'+phone[6:10]
#         users = User.objects.filter(phone=phone)
#         print users
#         if len(users) > 0:
#             show_name, show_id = None, None
#             for user in users:
#                 # inactivate
#                 if user.is_active:
#                     # log
#                     print user
#                     show_name = user.name
#                     show_id = user.userid
# 
#                     # save inactivation
#                     user.is_active = False
#                     user.save()
# 
#                     # send email
#                     send_mail('WattTime account inactivated',
#                               messages.account_inactivated_message(user.userid,
#                                                                   user.name,
#                                                                   user.phone).msg,
#                               EMAIL_HOST_USER,
#                               [user.email],
#                               fail_silently=False)
# 
#             if show_name:
#                 return render(request, 'accounts/unsubscribe_success.html', {
#                         'phone': phone,
#                         'name': show_name,
#                         'userid': show_id,
#                         })
#             else:
#                 return render(request, 'accounts/unsubscribe_fail.html', {
#                         'phone': phone,
#                         })
#         else:
#             return render(request, 'accounts/unsubscribe_fail.html', {
#                     'phone': phone,
#                     })
#     else:
#         return render(request, 'accounts/unsubscribe_fail.html', {
#                 'phone': phone,
#                 })
# 
# def user_profile(request):
# 	pass
# #@login_required
# #def profile_edit(request):
# #    success = False
# #    user = User.objects.get(pk=request.user.id)
# #    if request.method == 'POST':
# #        upform = UserProfileForm(request.POST, instance=user.get_profile())
# #        if upform.is_valid():
# #            up = upform.save(commit=False)
# #            up.user = request.user
# #            up.save()
# #            success = True
# #    else:
# #        upform = UserProfileForm(instance=user.get_profile())
# #    return render_to_response('profile/index.html',
# #        locals(), context_instance=RequestContext(request))
