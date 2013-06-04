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
from accounts.models import User, UserProfile
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from workers.models import SMSLog

def recurring_events(request):
    ''' Called every 5 min with a GET request'''
    # update and query BAs
    updated_bas = update_all(request)
    newest_timepoints = [BA_MODELS[ba].objects.all().latest('date') for ba in updated_bas]
    percent_greens = [point.fraction_green() * 100.0 for point in newest_timepoints]
    percent_coals = [point.fraction_high_carbon() * 100.0 for point in newest_timepoints]
    marginal_fuels = []
    for point in newest_timepoints:
        try:
            marginal_name = ne_fuels[point.marginal_fuel]
        except TypeError: # point.marginal_fuel is None
            marginal_name = 'None'
        marginal_fuels.append(marginal_name)

    print updated_bas, percent_greens, percent_coals, marginal_fuels

    # loop over users
    for up in UserProfile.objects.all():
        # get matching user
        user = up.userid
        print user

        # check if it's a good time
        localtime = user.local_now()
        if is_good_time_to_message(localtime, user.userid):
            # get message
            ba_ind = updated_bas.index(BALANCING_AUTHORITIES[user.state])
            msg = up.get_personalized_message(percent_greens[ba_ind],
                                              percent_coals[ba_ind],
                                              marginal_fuels[ba_ind])
            print msg, user.twilio_format_phone()

            # send text
            # UNCOMMENT NEXT LINE
            #send_text(msg, to=user.phone)
            
            # save to log
            logitem = SMSLog(user=user,
                             utctime=localtime,
                             localtime=localtime,
                             message=msg)
            logitem.save()
            print logitem.pk

    # return
    url = reverse('home')
    return HttpResponseRedirect(url)

def is_good_time_to_message(timestamp, userid):
    """ Returns True if hour/day are ok for user,
    and if they haven't received a message too recently.
    Returns False if not ok.
    """
    current_hour = timestamp.hour

    # bools
    hour_test = current_hour > 8 and current_hour < 22
    recent_test = True 
    # UNCOMMENT NEXT LINE
    #recent_test = timestamp - SMSLog.objects.filter(user=userid).latest('utctime').localtime > timedelta(hours=1)
    
    if hour_test and not recent_test:
        return True
    else:
        return False
