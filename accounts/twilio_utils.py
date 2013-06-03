from twilio.rest import TwilioRestClient
from datetime import date
from accounts.models import UserProfile

def send_text(msg, to):
    """ Send a text message to a phone number.
        Return success status (True or False).
    """
    # TO DO: add twilio vars to settings.py
    try:
        client = TwilioRestClient(account=TWILIO_ACCOUNT_SID,
                                  token=TWILIO_AUTH_TOKEN)
        client.sms.messages.create(to=to,
                                   from_=WATTTIME_PHONE,
                                   body=msg)
        return True
    except:
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
    
def is_correct_verification(msg, expected code):
    """ Return True if verification code is correct, 
        False if not.
    """
    # TO DO
    return True

