from django.conf import settings
from django.conf.urls.defaults import *
from django.views.generic import TemplateView


if getattr(settings, 'INVITATION_USE_ALLAUTH', False):
    from allauth.account.forms import BaseSignupForm as RegistrationFormTermsOfService
    reg_backend = 'allauth.account.auth_backends.AuthenticationBackend'
else:
    from registration.forms import RegistrationFormTermsOfService
    reg_backend = 'registration.backends.default.DefaultBackend'
    
from invitation.views import invite, invited, register, send_bulk_invitations, token

urlpatterns = patterns('',
    url(r'^invite/complete/$',
                TemplateView.as_view(template_name='invitation/invitation_complete.html'),
                name='invitation_complete'),
    url(r'^invite/$',
                invite,
                name='invitation_invite'),
    url(r'^invite/bulk/$',
                send_bulk_invitations,
                name='invitation_invite_bulk'),
    url(r'^invited/(?P<invitation_key>\w+)&(?P<invitation_recipient>\S+@\S+)?/$', 
                invited,
                name='invitation_invited'),
    url(r'^register/$',
                register,
                { 'backend': reg_backend },
                name='registration_register'),
    url(r'^token/(?P<key>\w+)/$', 
                token,
                name='invitation_token'),
)
