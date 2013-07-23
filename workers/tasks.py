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
from windfriendly.models import MARGINAL_FUELS, CAISO, NE
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS
import accounts.models
from accounts.regions import california, newengland
from accounts.twilio_utils import send_text
from accounts.models import UserProfile
from accounts.messages import morning_forecast_email, morning_forecast_email_first, ne_message_dirty_daytime, ne_message_dirty_evening, ne_message_clean
from workers.utils import debug, send_daily_report, perform_scheduled_tasks, schedule_task, send_ca_texts, add_to_report
from workers.models import latest_by_category, LastMessageSent
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
    perform_scheduled_tasks()
    send_ne_texts_if_necessary()
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

def this_hour():
    now = datetime.datetime.now(pytz.utc)
    return now.replace(minute = 0, second = 0, microsecond = 0)

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
    send_ca_forecast_emails()
    prepare_to_send_ca_texts()
    send_daily_report()

def send_ca_forecast_emails():
    # Send morning forecasts to california users.
    now = this_hour()
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
                send_mail(subj, msg, EMAIL_HOST_USER, [up.email])

def prepare_to_send_ca_texts():
    now = this_hour()

    # Dirty texts
    start = now.replace(hour = 15) # This is 8am PST
    end = start + datetime.timedelta(hours = 14) # This is 10pm PST

    rows = CAISO.best_guess_points_in_date_range(start, end)
    worst_time = min(rows, key = (lambda r : r.fraction_green())).date

    schedule_task(worst_time, "workers.utils.send_ca_texts(0)")

    add_to_report('Scheduled "dirty" texts to go out at {}'.format(worst_time))

    # Clean texts
    start = now.replace(hour = 0) + datetime.timedelta(days = 1) # This is 5pm PST
    end = start + datetime.timedelta(hours = 5) # This is 10pm PST

    rows = CAISO.best_guess_points_in_date_range(start, end)
    best_time = max(rows, key = (lambda r : r.fraction_green())).date

    schedule_task(best_time, "workers.utils.send_ca_texts(1)")

    add_to_report('Scheduled "clean" texts to go out at {}'.format(best_time))

def send_ne_texts_if_necessary():
    now = datetime.datetime.now(pytz.utc)
    ne_tz = pytz.timezone('America/New_York')
    now_ne = ne_tz.normalize(now.astimezone(ne_tz))

    is_weekday = (now_ne.isoweekday() <= 5)
    is_daytime = (9 <= now_ne.hour < 17)
    is_evening = (17 <= now_ne.hour < 22)

    fuel = NE.latest_point().marginal_fuel
    fuel_name = MARGINAL_FUELS[fuel]
    # 0 = coal
    # 1 = oil
    # 2 = natural gas
    # 3 = refuse
    # 4 = hydro
    # 5 = wood
    # 6 = nuclear
    # 7 = solar
    # 8 = wind
    # 9 = none
    dirty_fuel = [0, 1]
    clean_fuel = [8, 7, 6, 5, 4]

    is_dirty = fuel in dirty_fuel
    is_clean = fuel in clean_fuel

    # No more than one message in each 12 hour period
    last_okay_time = now - datetime.timedelta(hours = 20)

    ups = UserProfile.objects.all()

    # Dirty texts, working hours
    if is_weekday and is_daytime and is_dirty:
        last_msg = latest_by_category(LastMessageSent.NE_dirty_daytime)
        if last_msg is None or last_msg.date < last_okay_time:
            if last_msg is None:
                last_msg = LastMessageSent()
                last_msg.category = LastMessageSent.NE_dirty_daytime
            last_msg.date = now
            last_msg.save()

            debug("Sending NE texts for dirty, working hours {}".format(last_msg.date))

            for up in ups:
                if up.user.is_active and up.is_verified and up.region() == newengland:
                    if up.get_region_settings().message_frequency == 0:
                        message = ne_message_dirty_daytime(up, fuel_name)
                        res = send_text(message, up)

                        msg = 'Sent text "{}" to {}'.format(message.msg, up)
                        if not res:
                            msg = "FAILED: " + msg
                        debug(msg)
                        add_to_report(msg)

    # Dirty texts, after hours
    if is_dirty and (is_evening or (is_daytime and (not is_weekday))):
        last_msg = latest_by_category(LastMessageSent.NE_dirty_evening)
        if last_msg is None or last_msg.date < last_okay_time:
            if last_msg is None:
                last_msg = LastMessageSent()
                last_msg.category = LastMessageSent.NE_dirty_evening
            last_msg.date = now
            last_msg.save()

            debug("Sending NE texts for dirty, after hours {}".format(last_msg.date))

            for up in ups:
                if up.user.is_active and up.is_verified and up.region() == newengland:
                    if up.get_region_settings().message_frequency == 1:
                        message = ne_message_dirty_evening(up, fuel_name)
                        res = send_text(message, up)

                        msg = 'Sent text "{}" to {}'.format(message.msg, up)
                        if not res:
                            msg = "FAILED: " + msg
                        debug(msg)
                        add_to_report(msg)

    # Clean texts, after hours
    if is_clean and (is_evening or (is_daytime and (not is_weekday))):
        last_msg = latest_by_category(LastMessageSent.NE_clean)
        if last_msg is None or last_msg.date < last_okay_time:
            if last_msg is None:
                last_msg = LastMessageSent()
                last_msg.category = LastMessageSent.NE_clean
            last_msg.date = now
            last_msg.save()

            debug("Sending NE texts for clean {}".format(last_msg.date))

            for up in ups:
                if up.user.is_active and up.is_verified and up.region() == newengland:
                    if up.get_region_settings().message_frequency == 2:
                        message = ne_message_clean(up, fuel_name)
                        res = send_text(message, up)

                        msg = 'Sent text "{}" to {}'.format(message.msg, up)
                        if not res:
                            msg = "FAILED: " + msg
                        debug(msg)
                        add_to_report(msg)

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
