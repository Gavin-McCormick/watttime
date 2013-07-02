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


from windfriendly.models import debug
from datetime import datetime, timedelta, date
from accounts.models import SENDTEXT_TIMEDELTAS
from sms_tools.models import TwilioSMSEvent
from random import randint


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
