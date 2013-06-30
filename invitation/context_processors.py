from django.conf import settings
from invitation.models import InvitationKey

 
def remaining_invitations(request):
    """
    remaining_invitations: determines if the user has any invitations remaining.
    """
    if request.user.is_authenticated():
        remaining_invitations = InvitationKey.objects.remaining_invitations_for_user(request.user)
    else:
        remaining_invitations = None
    return {'remaining_invitations': remaining_invitations,}