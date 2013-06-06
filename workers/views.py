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


from datetime import datetime, timedelta, date
from dateutil import tz
import pytz
from windfriendly.views import update_all
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS
from windfriendly.parsers import ne_fuels
from accounts.twilio_utils import send_text
from accounts.models import User, UserProfile, SENDTEXT_TIMEDELTAS
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from workers.models import SMSLog
from random import randint

def recurring_events(request):
    ''' Called every 5 min with a GET request'''
    # update and query BAs
    updated_bas = update_all(request)
    newest_timepoints = [BA_MODELS[ba].objects.all().latest('date') for ba in updated_bas]
    percent_greens = [point.fraction_green() * 100.0 for point in newest_timepoints]
    percent_coals = [point.fraction_high_carbon() * 100.0 for point in newest_timepoints]
    marginal_fuels = [point.marginal_names() for point in newest_timepoints]

    print updated_bas, percent_greens, percent_coals, marginal_fuels

    # loop over users
    for up in UserProfile.objects.all():
        # get matching user
        user = up.userid
        print user, user.is_verified, user.is_active

        # check if it's a good time
        localtime = user.local_now()
        if is_good_time_to_message(localtime, user.userid, up) and (
            user.is_verified and user.is_active):
            # get message
            ba_ind = updated_bas.index(BALANCING_AUTHORITIES[user.state])
            msg = up.get_personalized_message(percent_greens[ba_ind],
                                              percent_coals[ba_ind],
                                              marginal_fuels[ba_ind])
            print user.phone, msg

            if msg:
                # send text
                send_text(msg, to=user.phone)
            
                # save to log
                logitem = SMSLog(user=user,
                                 utctime=now(),
                                 localtime=localtime,
                                 message=msg)
                logitem.save()

    # return
    url = reverse('home')
    return HttpResponseRedirect(url)

def is_good_time_to_message(timestamp, userid, user_profile,
                            min_hour=8, max_hour=22, do_rand=True):
    """ Returns True if hour/day are ok for user,
    and if they haven't received a message too recently,
    and if this time is randomly selected.
    Returns False if not ok.
    """
    # is it a good time of day to text?
    is_good_hour = timestamp.hour >= min_hour and timestamp.hour < max_hour

    # has the user been texted recently?
    text_period_secs = SENDTEXT_TIMEDELTAS[user_profile.text_freq].seconds
    if SMSLog.objects.filter(user=userid).exists():
        is_recently_notified = (timestamp - SMSLog.objects.filter(user=userid).latest('utctime').localtime).seconds < text_period_secs / 2
    else:
        is_recently_notified = False

    # add some noise
    if do_rand:
        n_5min_intervals = text_period_secs / 60 / 5
        is_randomly_selected = randint(1, n_5min_intervals) == 1
    else:
        is_randomly_selected = True

    # return bool
    if is_good_hour and (not is_recently_notified) and is_randomly_selected:
        return True
    else:
        return False
