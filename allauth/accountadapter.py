from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.exceptions import ImmediateHttpResponse
from allauth.account.utils import setup_user_email
from django.conf import settings
from invitation.models import InvitationKey
from invitation.backends import InvitationBackend
from django.contrib.auth.models import Group 
from allauth.account.signals import user_signed_up
from django.dispatch import receiver 
from django.views.generic.simple import direct_to_template

# https://github.com/arctelix/django-invitation/blob/master/docs/allauth%20integration.txt

class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        
        if getattr(settings, 'ALLOW_NEW_REGISTRATIONS', False):
            if getattr(settings, 'INVITE_MODE', False):
                invitation_key = request.session.get('invitation_key', False)
                if invitation_key:
                    if InvitationKey.objects.is_key_valid(invitation_key.key):
                        invitation_email = request.session.get('invitation_email', False)
                        print 'account adapter invitation_email: ',invitation_email
                        self.stash_verified_email(request, invitation_email)
                        return True
                    else:
                        extra_context = request.session.get('invitation_context', {})
                        template_name = 'invitation/wrong_invitation_key.html'
                        raise ImmediateHttpResponse(direct_to_template(request, template_name, extra_context))
            else:
                return True
        return False

    @receiver (user_signed_up)
    def complete_signup(sender, **kwargs):
        user = kwargs.pop('user')
        request = kwargs.pop('request')
        sociallogin = request.session.get('socialaccount_sociallogin', None)
        # Handle user permissions
        user.groups.add(Group.objects.get(name=settings.DEFAULT_USER_GROUP))
        user.save()
        # Handle invitation if required
        if 'invitation_key' in request.session.keys():
            invitation_key = request.session.get('invitation_key', False)
            invitation_key.mark_used(user)
            del request.session['invitation_key']
            del request.session['invitation_email']
            del request.session['invitation_context']
        print(user.username, ": has signed up!")
        

class SocialAccountAdapter(DefaultSocialAccountAdapter):

    def pre_social_login(self, request, sociallogin):
        # add sociallogin to session, because sometimes it's not there...
        request.session['socialaccount_sociallogin'] = sociallogin