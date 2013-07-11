import accounts.regions
import accounts.twilio_utils
import accounts.messages
import accounts.forms
import accounts.models
import accounts.views

UP = accounts.models.UserProfile

users_ = (lambda : list(UP.objects.all()))

msg_less = accounts.messages.Message.use_less_message
msg_more = accounts.messages.Message.use_more_message

def valid(up):
    return up.user.is_active and up.is_verified and up.state == 'CA'
