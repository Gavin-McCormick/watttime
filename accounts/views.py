from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from accounts.models import NewUserForm, User, UserProfileForm, UserPhoneForm
from django.core.urlresolvers import reverse

def profile_create(request):
    # process submitted form
    if request.method == 'POST':
        form = NewUserForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            new_user = form.save()

            # redirect
            if new_user.is_valid_state():
                # to alpha sign-up
                url = reverse('phone_setup', kwargs={'userid': new_user.id})
                return HttpResponseRedirect(url)
            else:
                # to generic thanks
                url = reverse('thanks')
                return HttpResponseRedirect(url)
    else:
        form = NewUserForm() # An unbound form

    # display form
    return render(request, 'index.html', {'form': form})

def profile_alpha(request, userid):
    # process submitted form
    if request.method == 'POST':
        form = UserProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            new_profile = form.save(commit=False)
            new_profile.userid = User.objects.get(pk=userid)
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

def phone_setup(request, userid):
    # process submitted form
    if request.method == 'POST':
        form = UserPhoneForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            profile = User.objects.get(pk=userid)
            print profile
            profile.phone = form.phone
            print profile.phone
            profile.save()

            # redirect
            url = reverse('phone_verify', kwargs={'userid': user.id})
            return HttpResponseRedirect(url)
    else:
        form = UserPhoneForm() # An unbound form

    # display form
    return render(request, 'accounts/phone_setup.html', {
            'form': form,
            'userid': userid,
    })
	
def phone_verify(request, userid):
    return render(request, 'accounts/phone_verify.html')

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
