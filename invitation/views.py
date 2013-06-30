from django.conf import settings
from django.shortcuts import render
from django.template.loader import render_to_string, get_template
from django.core.urlresolvers import reverse
from django.http import HttpResponseRedirect
from django.contrib.auth.decorators import login_required
from django.contrib.sites.models import Site
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib import messages
from django.utils.safestring import mark_safe

if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
    from allauth.socialaccount.views import signup as allauth_signup
    from allauth.socialaccount.forms import SignupForm as RegistrationForm
    registration_template = 'accounts/signup.html'
    
    def registration_register(request, backend, success_url, form_class, disallowed_url, template_name, extra_context):
        return allauth_signup(request, template_name=template_name)
else:        
    from registration.views import register as registration_register
    from registration.forms import RegistrationForm
    registration_template = 'registration/registration_form.html'

from invitation.models import InvitationKey
from invitation.forms import InvitationKeyForm
from invitation.backends import InvitationBackend

is_key_valid = InvitationKey.objects.is_key_valid
get_key = InvitationKey.objects.get_key
remaining_invitations_for_user = InvitationKey.objects.remaining_invitations_for_user

def invited(request, invitation_key=None, invitation_recipient=None, extra_context=None):
    if getattr(settings, 'INVITE_MODE', False):
        extra_context = extra_context is not None and extra_context.copy() or {}
        template_name = 'invitation/wrong_invitation_key.html'
        if invitation_key:
            extra_context.update({'invitation_key': invitation_key})
            valid_key_obj = is_key_valid(invitation_key)
            if valid_key_obj:
                template_name = 'invitation/invited.html'
                invitation_recipient = valid_key_obj.recipient or invitation_recipient
                #convert any old invitation email to new format
                if not isinstance(invitation_recipient, tuple):
                    invitation_recipient = (invitation_recipient, None, None)
                extra_context.update({'invitation_recipient': invitation_recipient})
                request.session['invitation_key'] = valid_key_obj
                request.session['invitation_recipient'] = invitation_recipient
                request.session['invitation_context'] = extra_context or {}

        return render(request, template_name, extra_context)
    else:
        return HttpResponseRedirect(reverse('registration_register'))

def register(request, backend, success_url=None,
            form_class=RegistrationForm,
            disallowed_url='registration_disallowed',
            post_registration_redirect=None,
            template_name=registration_template,
            wrong_template_name='invitation/wrong_invitation_key.html',
            extra_context=None):
    
    extra_context = extra_context is not None and extra_context.copy() or {}
    if getattr(settings, 'INVITE_MODE', False):
        invitation_key = request.REQUEST.get('invitation_key', False)
        if invitation_key:
            extra_context.update({'invitation_key': invitation_key})
            if is_key_valid(invitation_key):
                return registration_register(request, backend, success_url,
                                            form_class, disallowed_url,
                                            template_name, extra_context)
            else:
                extra_context.update({'invalid_key': True})
        else:
            extra_context.update({'no_key': True})
        return render(request, wrong_template_name, extra_context)
    else:
        return registration_register(request, backend, success_url, form_class,
                                     disallowed_url, template_name, extra_context)

#TODO: add sender_note to form 
def invite(request, success_url=None,
            form_class=InvitationKeyForm,
            template_name='invitation/invitation_form.html',
            extra_context=None):
    extra_context = extra_context is not None and extra_context.copy() or {}
    remaining_invitations = remaining_invitations_for_user(request.user)
    print remaining_invitations, request.user
    if request.method == 'POST':
        form = form_class(data=request.POST, files=request.FILES, 
                          remaining_invitations=remaining_invitations, 
                          user=request.user)
        if form.is_valid():
            recipient = form.cleaned_data["recipient"]
            sender_note = form.cleaned_data["sender_note"]
            invitation = InvitationKey.objects.create_invitation(request.user, recipient)
            invitation.send_to(sender_note=sender_note)
            # success_url needs to be dynamically generated here; setting a
            # a default value using reverse() will cause circular-import
            # problems with the default URLConf for this application, which
            # imports this file.
            return HttpResponseRedirect(success_url or reverse('invitation_complete'))
    else:
        form = form_class()
    invitation = InvitationKey.objects.create_invitation(request.user, save=False)
    preview_context = invitation.get_context('--your note will be inserted here--')
    extra_context.update({
            'form': form,
            'remaining_invitations': remaining_invitations,
            'email_preview': render_to_string('invitation/invitation_email.html', preview_context),
        })
    return render(request, template_name, extra_context)
invite = login_required(invite)


@staff_member_required
def send_bulk_invitations(request, success_url=None):
    current_site = Site.objects.get_current()
    if request.POST.get('post'):
        to_emails = [(e.split(',')[0].strip(),e.split(',')[1].strip() or None,e.split(',')[2].strip() or None) if e.find(',')+1 else (e.strip() or None, None, None) for e in request.POST['to_emails'].split(';')]
        #to_emails = [(e.split(',')[0],e.split(',')[1]) if e.find(',') else tuple('',e) for e in request.POST['to_emails'].split(';')]
        sender_note = request.POST['sender_note']
        from_email = request.POST['from_email']
        if len(to_emails)>0 and to_emails[0] != '': 
            for recipient in to_emails:
                if recipient[0]:
                    invitation = InvitationKey.objects.create_invitation(request.user, recipient)
                    try:
                        invitation.send_to(from_email, mark_safe(sender_note))
                    except:
                        messages.error(request, "Mail to %s failed" % recipient[0])
            messages.success(request, "Mail sent successfully")
            return HttpResponseRedirect(success_url or reverse('invitation_invite_bulk'))
        else:
            messages.error(request, 'You did not provied any email addresses.')
            return HttpResponseRedirect(reverse('invitation_invite_bulk'))
    else:
        invitation = InvitationKey.objects.create_invitation(request.user, save=False)
        preview_context = invitation.get_context('--your note will be inserted here--')
        
        context = {
            'title': "Send Bulk Invitations",
            'html_preview': render_to_string('invitation/invitation_email.html', preview_context),
            'text_preview': render_to_string('invitation/invitation_email.txt', preview_context),
        }
        return render(request, 'invitation/invitation_form_bulk.html',
            context)

from django.shortcuts import redirect
from django.core.files.storage import default_storage
import urllib2
import mimetypes
from django.http import HttpResponse
from urlparse import urlparse, urlunparse
            
def token(request, key):
    '''
    Returns an aproproate token image.  If the key is valid & token image existis a personalized
    token is returned or else a token image marked invalid is returned.
    '''
    print  '---token'
    site = Site.objects.get_current()
    scheme = 'http'
    if request.is_secure():
        scheme = 'https'
    root_url = '%s://%s' % (scheme, site.domain)
    r_parse = urlparse(root_url, scheme)
    s_parse = urlparse(settings.STATIC_URL, scheme)
    m_parse = urlparse(settings.MEDIA_URL, scheme)
    s_parts = (s_parse.scheme, s_parse.netloc or r_parse.netloc, s_parse.path, s_parse.params, s_parse.query, s_parse.fragment)
    static_url = urlunparse(s_parts)
    m_parts = (m_parse.scheme, m_parse.netloc or r_parse.netloc, m_parse.path, m_parse.params, m_parse.query, m_parse.fragment)
    media_url = urlunparse(m_parts)
    print 'static_url', static_url
    print 'media_url', media_url
        
    token_url = '%stokens/%s.png' % (media_url, key)
    print token_url
    token_invalid_url = '%snotification/img/%s.png' % (static_url, 'token-invalid')
    token_path = 'tokens/%s.png' % key
    valid_key = is_key_valid(key) or key == 'previewkey00000000'
    if default_storage.exists(token_path) and valid_key:
        contents = urllib2.urlopen(token_url).read()
        mimetype = mimetypes.guess_type(token_url)
        response = HttpResponse(contents, mimetype=mimetype)
    else:
        contents = urllib2.urlopen(token_invalid_url).read()
        mimetype = mimetypes.guess_type(token_invalid_url)
        response = HttpResponse(contents, mimetype=mimetype)
    
    return response
    