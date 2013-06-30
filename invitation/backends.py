from django.conf import settings
if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
    from allauth.account.auth_backends import AuthenticationBackend as DefaultBackend
else:
    from registration.backends.default import DefaultBackend

from invitation.models import InvitationKey

class InvitationBackend(DefaultBackend):

    def post_registration_redirect(self, request, user, *args, **kwargs):
        """
        Return the name of the URL to redirect to after successful
        user registration.

        """
        invitation_key = request.REQUEST.get('invitation_key')
        key = InvitationKey.objects.get_key(invitation_key)
        if key:
            key.mark_used(user)
            
            # delete it from the session too
            del request.session['invitation_key']

        return ('registration_complete', (), {})
