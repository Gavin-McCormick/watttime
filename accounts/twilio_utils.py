from twilio.rest import TwilioRestClient
from datetime import date
from accounts.models import UserProfile
from settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WATTTIME_PHONE
from windfriendly.models import debug
from sms_tools.models import TwilioSMSEvent
from accounts.messages import Message

def send_text(msg, up):
    """ Send a text message to a phone number.
        Return success status (True or False).
    """
    try:
        client = TwilioRestClient(account=TWILIO_ACCOUNT_SID,
                                  token=TWILIO_AUTH_TOKEN)
        c = client.sms.messages.create(to=up.phone,
                                   from_=WATTTIME_PHONE,
                                   body=msg.msg)
        TwilioSMSEvent(user=up.user,
                       msg_type=msg.msg_type,
                       to_number=up.phone,
                       from_number=WATTTIME_PHONE,
                       body=msg.msg).save()

        debug("texted '{}' to {}".format(msg, str(up.name)))
        return True
    except:
        print ("Faild message", up.phone, WATTTIME_PHONE, msg.msg)
        debug("failed to text '{}' to {}".format(msg, str(up.name)))
        raise
        return False
