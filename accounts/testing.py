import settings
import urls
import accounts.config
import accounts.forms
import accounts.messages
import accounts.models
import accounts.regions
import accounts.tests
import accounts.twilio_utils
import accounts.views
import pages.context_processors
import pages.models
import pages.tests
import pages.views
import sms_tools.models
import sms_tools.views
import watttime_shift.models
import watttime_shift.tests
import watttime_shift.views
import windfriendly.api
import windfriendly.balancing_authorities
import windfriendly.managers
import windfriendly.models
import windfriendly.parsers
import windfriendly.settings
import windfriendly.tests.test_api
import windfriendly.tests.test_models
import windfriendly.urls
import windfriendly.utils
import windfriendly.views
import workers.models
import workers.utils
import workers.tasks
import workers.views

import datetime
import pytz

now_ = (lambda : datetime.datetime.now(pytz.utc))
timedelta = datetime.timedelta

UP = accounts.models.UserProfile

users_ = (lambda : list(UP.objects.all()))

msg_less = accounts.messages.Message.use_less
msg_more = accounts.messages.Message.use_more

def valid(up):
    return up.user.is_active and up.is_verified and up.state == 'CA'

def users_mf(mf):
    l = []
    for up in users_():
        if valid(up) and up.get_region_settings().message_frequency == mf:
            l.append(up)
    return l

send_text = accounts.twilio_utils.send_text


KV = workers.models.KeyValue
ST = workers.models.ScheduledTasks
DR = workers.models.DailyReport
DM = workers.models.DebugMessage
LMS = workers.models.LastMessageSent

def dump_model(m):
    for x in m.objects.all():
        print (x)
