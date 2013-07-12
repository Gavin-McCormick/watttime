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

# regular imports
from django.core.mail import send_mail
from windfriendly.models import debug, MARGINAL_FUELS, CAISO
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS
from accounts.twilio_utils import send_text
from accounts.models import UserProfile
from accounts.messages import morning_forecast_email, morning_forecast_email_first
from workers.utils import is_good_time_to_message
import datetime
import pytz

# XXX
# Why does this not work? !!!!
# import settings

from settings import EMAIL_HOST_USER

def run_frequent_tasks():
    """ Should be run every 5-10 min by a clock process or scheduler """
    # scrape new info from utilities
    updated_bas = update_bas(['BPA', 'ISONE'])
    print updated_bas

    # send notifications to users in updated regions
   # notified_users = send_text_notifications(['ISONE'])
   # print notified_users

def run_hourly_tasks():
    """ Should be run every hour by a clock process or scheduler """
    # scrape new info from utilities
    updated_bas = update_bas(['CAISO'])
    print updated_bas

    # send notifications to users in updated regions
   # notified_users = send_text_notifications(['CAISO'])
   # print notified_users

def round_to_hour(dt):
    hour = dt.hour
    if dt.minute >= 30:
        hour += 1
    return (hour % 24)

def display_hour_pst(dt):
    hour = (round_to_hour(dt) + 17) % 24
    if hour < 12:
        return '{:d}am'.format(hour)
    elif hour == 12:
        return 'noon'
    else:
        return '{:d}pm'.format(hour - 12)

# Run at 14.00 UTC every day
def run_daily_tasks_1400():
    # Send morning forecasts to california users.
    now = datetime.datetime.now(pytz.utc).replace(minute = 0, second = 0, microsecond = 0)
    start = now.replace(hour = 14) # This is 7am PST
    end = start + datetime.timedelta(hours = 16) # This is 11pm PST

    rows = CAISO.best_guess_points_in_date_range(start, end)
    best_time = max(rows, key = (lambda r : r.fraction_green())).date
    worst_time = min(rows, key = (lambda r : r.fraction_green())).date

    best_hour = display_hour_pst(best_time)
    worst_hour = display_hour_pst(worst_time)

    subj = 'WattTime {} forecast: {} cleanest, {} dirtiest'
    subj = subj.format(start.strftime('%m/%d'), best_hour, worst_hour)
    # subj = 'WattTime forecast #1'

    for up in UserProfile.objects.all():
        if up.user.is_active and up.state == 'CA':
            ca = up.get_region_settings()
            if ca.forecast_email:
                # Send email to that user.
                msg = morning_forecast_email(up.name, best_hour, worst_hour)
                # msg = morning_forecast_email_first(up.name, best_hour, worst_hour)
                # send_mail(subj, msg, EMAIL_HOST_USER, [up.email])

    send_mail(subj, msg, EMAIL_HOST_USER, ['eric.stansifer@gmail.com'])

def update_bas(bas):
    # update and query BAs
    updates = [BA_PARSERS[ba]().update() for ba in bas]

    # log
    newest_timepoints = [BA_MODELS[ba].latest_point() for ba in bas]
    marginal_fuels = [MARGINAL_FUELS[point.marginal_fuel] for point in newest_timepoints]
    debug("ping called (marginal fuel {})".format(marginal_fuels[0]))

    # return
    return updates

def send_text_notifications(bas):
    """ Should be run every 5-10 min, after updating BAs """
    # get newest info
    newest_timepoints = [BA_MODELS[ba].latest_point() for ba in bas]
    percent_greens = [point.fraction_green() * 100.0 for point in newest_timepoints]
    percent_coals = [point.fraction_high_carbon() * 100.0 for point in newest_timepoints]
    marginal_fuels = [MARGINAL_FUELS[point.marginal_fuel] for point in newest_timepoints]
    print [tp.date for tp in newest_timepoints]

    # loop over users
    notified_users = []
    for up in UserProfile.objects.all():
        # get matching user
        debug("  looking at user {} ({}): verified? {} active? {}".format(up.name,
                str(up.phone), str(up.is_verified), str(up.user.is_active)))

        # check if user in region to be notified
        user_ba = BALANCING_AUTHORITIES[up.state]
        if user_ba in bas:
            ba_ind = bas.index(user_ba)
        else:
            continue

        # check if it's a good time
        localtime = up.local_now()
        if (up.is_verified and up.user.is_active and
                is_good_time_to_message(localtime, up.user_id, up)):
            debug("    is verified, is active, and is good time to message")
        else:
            debug('    either not verified, not active, or not good time to message')
            continue

        # get message
        # TODO: method does not exist!
        msg = up.get_personalized_message(percent_greens[ba_ind],
                                          percent_coals[ba_ind],
                                          marginal_fuels[ba_ind])

        # send notification
        print msg
        if msg:
            if len(msg) <= 140:
                debug('      sending message!')
                # send text
                send_text(msg, to=up.user)

                notified_users.append(up.user_id)
            else:
                debug('      Failed to send message "{}" as it is too long.'.format(msg))
        else:
            debug('      active, verified user, but not right fuel now')

    # return
    return notified_users
