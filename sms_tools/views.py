import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio import twiml

from accounts.models import User
from sms_tools.models import TwilioSMSEvent
from settings import WATTTIME_PHONE

# TODO learn if there are standards for how to normalize
# phone numbers
#
# There is a python-phonenumbers package, maybe that is better....

# Assumes US number if unspecified.
def normalize_phone_number(phonenumber):
    out = []
    for char in phonenumber:
        if char == '+' and len(out) == 0:
            # Leading +
            out.append(char)
        elif char in "0123456789":
            if len(out) == 0:
                # No leading +, assume US
                out = ['+', '1']
            elif char == '1' and out == ['+', '1']:
                # US number with leading 1 but no +
                continue
            out.append(char)
    return ''.join(out)

@csrf_exempt
@require_http_methods(['POST'])
def twilio_endpoint(request):
    """Handle incoming twilio messages"""

    from_number = request.POST.get('From', None)
    to_number   = request.POST.get('To', None)
    body        = request.POST.get('Body', None)

    norm_from_number = norm_from_number(from_number)
    user = None
    for user_ in User.objects.all():
        up = user.get_profile()
        if up.is_verified and norm_from_number == normalize_phone_number(up.phone):
            user = user_
            break

    last_text = None
    if user is not None:
        texts = TwilioSMSEvent.objects.filter(user=user, from_number=WATTTIME_PHONE)
        if texts:
            last_text = texts.latest('created_at')

    TwilioSMSEvent(user=user,
                   to_number=to_number,
                   from_number=from_number,
                   body=body,
                   msg_type=TwilioSMSEvent.INCOMING,
                   response_to=last_text).save()

    resp = twiml.Response()
    return HttpResponse(unicode(resp).encode('utf-8'), content_type='application/xml')
