import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from twilio import twiml

from accounts.twilio_utils import get_latest_sent_text
from accounts.models import User
from sms_tools.models import TwilioSMSEvent
from settings import WATTTIME_PHONE

@csrf_exempt
@require_http_methods(['POST'])
def twilio_endpoint(request):
    """Handle incoming twilio messages"""

    params = json.loads(request.body)
    from_number = params['From']
    from_number = "%s-%s-%s" % (from_number[2:5], from_number[5:8], from_number[8:12])
    to_number = params['To']
    body = params['Body']

    user = User.objects.filter(phone=from_number)[0]
    # get_latest should do a db lookup, not twilio
    last_text = TwilioSMSEvent.objects.filter(user=user, from_number=WATTTIME_PHONE).latest('created_at')


    TwilioSMSEvent(user=user,
                   to_number=to_number,
                   from_number=from_number,
                   body=body,
                   msg_type=TwilioSMSEvent.INCOMING,
                   response_to=last_text).save()
    
    resp = twiml.Response()
    return HttpResponse(unicode(resp).encode('utf-8'), content_type='application/xml')
