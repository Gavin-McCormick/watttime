from django.db import models
from django_localflavor_us.models import PhoneNumberField, USStateField

from django.contrib.auth.models import User
from accounts.messages import Message

class TwilioSMSEvent(models.Model):
    user = models.ForeignKey(User, null=True)
    response_to = models.ForeignKey('self', null=True)
    to_number = PhoneNumberField()
    from_number = PhoneNumberField()
    body = models.CharField(max_length=160)

    USE_LESS = Message.USE_LESS
    USE_MORE = Message.USE_MORE
    CONFIRMATION = Message.CONFIRMATION
    INFORMATION = Message.INFORMATION
    INCOMING = 'incoming_msg'

    msg_type_choices = (
            (USE_LESS, USE_LESS),
            (USE_MORE, USE_MORE),
            (CONFIRMATION, CONFIRMATION),
            (INFORMATION, INFORMATION),
            (INCOMING, INCOMING),
        )

    msg_type = models.CharField(max_length=20, choices = msg_type_choices)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
