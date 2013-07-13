# Copyright wattTime 2013
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Anna Schneider

from django.core.mail import send_mail
from accounts.messages import ca_message_dirty, ca_message_clean
from accounts.models import UserProfile
from workers.models import ScheduledTasks, DailyReport, DebugMessage
from datetime import datetime, timedelta, date
# from accounts.models import SENDTEXT_TIMEDELTAS
from sms_tools.models import TwilioSMSEvent
from random import randint
from settings import EMAIL_HOST_USER
import datetime
import pytz

def is_good_time_to_message(timestamp, user_id, user_profile,
                            min_hour=8, max_hour=22, do_rand=False):
    """ Returns True if hour/day are ok for user,
    and if they haven't received a message too recently,
    and if this time is randomly selected.
    Returns False if not ok.
    """
    # is it a good time of day to text?
    is_good_hour = timestamp.hour >= min_hour and timestamp.hour < max_hour

    # has the user been texted recently?
    text_period_secs = SENDTEXT_TIMEDELTAS[user_profile.message_frequency].total_seconds()
    user_sms_logs = TwilioSMSEvent.objects.filter(user=user_id)
    if user_sms_logs.exists():
        dt = (timestamp - user_sms_logs.latest('created_at').created_at).total_seconds()

        is_recently_notified = dt < text_period_secs / 2
    else:
        is_recently_notified = False
        dt = -1

    # add some noise
    if do_rand:
        n_5min_intervals = (text_period_secs / 60 / 5) / 3
        if n_5min_intervals < 1:
            n_5min_intervals = 1
        is_randomly_selected = randint(1, n_5min_intervals) == 1
    else:
        is_randomly_selected = True

    debug('    is good hour? {}, {:f} seconds since last message, {:f} seconds desired interval, recently notified? {}, randomly selected? {}'.format(str(is_good_hour), dt, text_period_secs, is_recently_notified, is_randomly_selected))

    if is_good_hour and (not is_recently_notified) and is_randomly_selected:
        print 'good'
        return True
    else:
        print 'bad'
        return False

def send_ca_texts(group):
    # group == 0: daily, dirty
    # group == 1: daily, clean
    # group == 2: less than daily
    # group == 3: emergencies only

    # We don't have messages for these groups yet.
    if not (group in [0, 1]):
        return

    for up in UserProfile.objects.all():
        if up.user.is_active and up.is_verified and up.state == 'CA':
            if up.get_region_settings().message_frequency == group:
                if group == 0:
                    message = ca_message_dirty(up)
                else: # group == 1
                    message = ca_message_clean(up)
                send_text(message, up)

def schedule_task(time, command):
    if len(command) >= 300:
        raise RuntimeError("Command string '{}' is too long.".format(command))

    t = ScheduledTask()
    t.date = time
    t.command = command
    t.save()

def perform_scheduled_tasks():
    # These might be needed by some commands
    import workers.tasks
    import workers.utils
    import workers.views
    import workers.models

    now = datetime.datetime.now(pytz.utc)
    for task in ScheduledTask.objects.all():
        if task.date < now:
            command = task.command
            exec (command) # Fixed in Python 3

def same_day(t1, t2):
    return t1.year == t2.year and t1.month == t2.month and t1.day == t2.day

def send_daily_report():
    now = datetime.datetime.now(pytz.utc)
    # targets = ['eric.stansifer@gmail.com', 'gavin.mccormick@gmail.com', 'annarschneider@gmail.com']
    targets = ['eric.stansifer@gmail.com']
    subj = 'WattTime daily report {}'.format(now.strftime('%Y.%m.%d'))
    message = []
    message.append('Report generated {} UTC'.format(now.strftime('%Y.%m.%d %H.%M')))

    events = []
    for dr in DailyReport.objects.all():
        event.append((dr.date, dr.message))
        dr.delete()
    events.sort()

    if len(events) == 0:
        message.append('No events since last report.')
    else:
        prev_date = None
        for event in events:
            cur_date = event[0]

            if prev_date is None or (not same_day(prev_date, cur_date)):
                message.append('')
                if same_day(cur_date, now):
                    message.append('Today:')
                elif same_day(cur_date + datetime.timedelta(days = 1), now):
                    message.append('Yesterday:')
                else:
                    message.append(cur_date.strftime('%Y.%m.%d:'))
            prev_date = cur_date

            message.append('[{}]:  {}'.format(cur_date.strftime('%H.%M'), event[1]))

    message = '\n'.join(message)

    send_mail(subj, message, EMAIL_HOST_USER, targets)

def add_to_report(message):
    event = DailyReport()
    event.date = datetime.datetime.now(pytz.utc)
    event.message = message
    event.save()

def debug(message):
    dm = DebugMessage()
    dm.date = datetime.datetime.now(pytz.utc)
    dm.message = message
    dm.save()
