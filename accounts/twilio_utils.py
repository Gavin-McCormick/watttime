import twilio
import twilio.rest
import sms_tools.models
from settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN, WATTTIME_PHONE
from workers.utils import debug, add_to_report

def send_text(msg, up, force = False):
    text = msg.msg
    if len(text) >= 160:
        m = "Failed to send text, too long. {} -> {!s}".format(text, up)
        debug(m)
        add_to_report(m)
        return False

    if not up.user.is_active:
        m = "Failed to send text, user inactive. {} -> {!s}.".format(text, up)
        debug(m)
        add_to_report(m)
        return False

    if not (force or up.is_verified):
        m = "Failed to send text, user not verified. {} -> {!s}.".format(text, up)
        debug(m)
        add_to_report(m)
        return False

    try:
        client = twilio.rest.TwilioRestClient(account = TWILIO_ACCOUNT_SID,
                token = TWILIO_AUTH_TOKEN)
        c = client.sms.messages.create(to = up.phone,
                from_ = WATTTIME_PHONE,
                body = text)
    except twilio.TwilioRestException as e:
        m = "Failed to send text, twilio exception '{!s}'. {} -> {!s}.".format(e, text, up)
        debug(m)
        add_to_report(m)
        return False

    sms_tools.models.TwilioSMSEvent(user = up.user,
            msg_type = msg.msg_type,
            to_number = up.phone,
            from_number = WATTTIME_PHONE,
            body = msg.msg).save()

    debug ("Sent text. {} -> {!s}.".format(text, up))

    return True
