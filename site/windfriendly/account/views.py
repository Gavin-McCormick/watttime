from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.contrib.auth.decorators import login_required

def login(request):
    return render_to_response('templates/login.html',
        locals(), context_instance=RequestContext(request))    

@login_required
def profile_show(request):
    pass

@login_required
def profile_create(request):
    pass

@login_required
def profile_edit(request):
    success = False
    user = User.objects.get(pk=request.user.id)
    if request.method == 'POST':
        upform = UserProfileForm(request.POST, instance=user.get_profile())
        if upform.is_valid():
            up = upform.save(commit=False)
            up.user = request.user
            up.save()
            success = True
    else:
        upform = UserProfileForm(instance=user.get_profile())       

    return render_to_response('profile/index.html',
        locals(), context_instance=RequestContext(request))
