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

# set up script to be run from command line
import os
import sys
path = os.path.normpath(os.path.join(os.getcwd(), '..'))
sys.path.append(path)
from django.core.management import setup_environ
import settings
setup_environ(settings)

# regular imports
from windfriendly.models import debug, MARGINAL_FUELS
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS
from accounts.twilio_utils import send_text
from accounts.models import UserProfile
from django.utils.timezone import now
from sms_tools.models import TwilioSMSEvent
from workers.utils import is_good_time_to_message

def run_frequent_tasks():
    """ Should be run every 5-10 min by a clock process or scheduler """
    # scrape new info from utilities
    updated_bas = update_bas(['BPA', 'ISONE'])
    print updated_bas

    # send notifications to users in updated regions
    notified_users = send_text_notifications(['ISONE'])
    print notified_users

def run_hourly_tasks():
    """ Should be run every hour by a clock process or scheduler """
    # scrape new info from utilities
    updated_bas = update_bas(['CAISO'])
    print updated_bas

    # send notifications to users in updated regions
    # notified_users = send_text_notifications(['CAISO'])
    # print notified_users

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
        user = up.userid
        debug("  looking at user {} ({}): verified? {} active? {}".format(user.name,
                str(user.phone), str(user.is_verified), str(user.is_active)))

        # check if user in region to be notified
        user_ba = BALANCING_AUTHORITIES[user.state]
        if user_ba in bas:
            ba_ind = bas.index(user_ba)
        else:
            continue

        # check if it's a good time
        localtime = user.local_now()
        if (user.is_verified and user.is_active and
                is_good_time_to_message(localtime, user.userid, up)):
            debug("    is verified, is active, and is good time to message")
        else:
            debug('    either not verified, not active, or not good time to message')
            continue

        # get message
        msg = up.get_personalized_message(percent_greens[ba_ind],
                                          percent_coals[ba_ind],
                                          marginal_fuels[ba_ind])

        # send notification
        if msg:
            if len(msg) >= 150:
                debug('      sending message!')
                # send text
                send_text(msg, to=user)

                notified_users.append(user.userid)
            else:
                debug('      Failed to send message "{}" as it is too long.'.format(msg))
        else:
            debug('      active, verified user, but not right fuel now')

    # return
    return notified_users

# MAIN
if __name__ == "__main__":
    run_frequent_tasks()