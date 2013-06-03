from django.shortcuts import render, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from accounts.models import NewUserForm, User, UserProfileForm, UserPhoneForm
from django.core.urlresolvers import reverse

def profile_create(request):
    # process submitted form
    if request.method == 'POST' and 'sign_up' in request.POST:
        form = NewUserForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            new_user = form.save()

            # redirect
            if new_user.is_valid_state():
                # to phone setup
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

def phone_setup(request, userid):
    # process submitted phone number
    user = get_object_or_404(User, pk=userid)
    if request.method == 'POST':
    	form = UserPhoneForm(request.POST, instance = user)
        if form.is_valid():# Check if the phone number entered is in the correct format
            form.save()
            # send text here!!! TO DO

            
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
    # process submitted form
    if request.method == 'POST':
        form = UserProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # save form
            goals = form.cleaned_data.get('goal')
            print goals
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

def phone_verify(request, userid):
    return render(request, 'accounts/phone_verify.html', {
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
