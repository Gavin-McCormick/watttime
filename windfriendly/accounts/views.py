from django.shortcuts import render
from django.template import RequestContext
from django.http import HttpResponseRedirect
#from django.contrib.auth.decorators import login_required
from windfriendly.accounts.models import NewUserForm, User, UserProfileForm
from django.core.urlresolvers import reverse

def profile_create(request):
    # process submitted form
    if request.method == 'POST':
        form = NewUserForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            new_user = form.save()
            if new_user.is_valid_state():
                url = reverse('profile_complete', kwargs={'userid': new_user.id})
                return HttpResponseRedirect(url) # Redirect after POST
            else:
                return render(request, 'accounts/sorry.html', {
                        'name': new_user.name,
                        'state': new_user.long_state_name(),
                        })
    else:
        form = NewUserForm() # An unbound form

    # display form
    return render(request, 'accounts/profile.html', {'form': form})

def profile_complete(request, userid):
    # process submitted form
    if request.method == 'POST':
        form = UserProfileForm(request.POST) # A form bound to the POST data
        if form.is_valid(): # All validation rules pass
            # Process the data in form.cleaned_data
            new_profile = form.save(commit=False)
            new_profile.userid = User.objects.get(pk=userid)
            new_profile.save()
            print 'got here?'
            return HttpResponseRedirect('/welcome/%s' % userid) # Redirect after POST
    else:
        form = UserProfileForm() # An unbound form

    # display form
    return render(request, 'accounts/update.html', {
            'form': form,
            'userid': userid,
    })

def welcome(request, userid):
    name = User.objects.get(pk=userid).name
    return render(request, 'accounts/welcome.html', {'name': name})

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
