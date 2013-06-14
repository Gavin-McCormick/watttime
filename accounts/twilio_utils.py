from twilio.rest import TwilioRestClient
from datetime import date
from accounts.models import UserProfile
from settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WATTTIME_PHONE
from windfriendly.models import debug

def send_text(msg, to):
    """ Send a text message to a phone number.
        Return success status (True or False).
    """
    try:
        client = TwilioRestClient(account=TWILIO_ACCOUNT_SID,
                                  token=TWILIO_AUTH_TOKEN)
        c = client.sms.messages.create(to=to,
                                   from_=WATTTIME_PHONE,
                                   body=msg)
        debug("texted '{}' to {}".format(msg, str(to)))
        return True
    except:
        debug("failed to text '{}' to {}".format(msg, str(to)))
        return False

def get_latest_text(from_):
    """ Receive today's most recent text message from a phone number.
        Return body of text message, or None.
    """
    client = TwilioRestClient(account=TWILIO_ACCOUNT_SID,
                              token=TWILIO_AUTH_TOKEN)
    messages = client.sms.messages.list(to=WATTTIME_PHONE,
                                        from_=from_,
                                        date_sent=date.today())
    try:
        return messages[0].body
    except IndexError:
        return None
