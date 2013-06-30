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
import json
import pytz
import traceback
from windfriendly.models import debug
from windfriendly.views import update, update_all
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS
from windfriendly.parsers import ne_fuels
from accounts.twilio_utils import send_text
from accounts.models import User, UserProfile, SENDTEXT_TIMEDELTAS
from accounts.messages import alpha_completed
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from django.utils.timezone import now
from workers.models import SMSLog
from django.core.mail import send_mail
from settings import EMAIL_HOST_USER
from random import randint

import accounts.models
import windfriendly.models
import workers.models

def demo(request):
    message = []

    update(request, 'ne')
    message.append('Updated latest New England data.')

    last = BA_MODELS['ISONE'].objects.all().latest('date')
    message.append('Natural Gas: {:.2f} MW'.format(last.gas))
    message.append('Nuclear: {:.2f} MW'.format(last.nuclear))
    message.append('Hydro: {:.2f} MW'.format(last.hydro))
    message.append('Coal: {:.2f} MW'.format(last.coal))
    message.append('Other renewable fuels: {:.2f} MW'.format(last.other_renewable))
    message.append('Other fossil fuels: {:.2f} MW'.format(last.other_fossil))
    marginal = ne_fuels[last.marginal_fuel]
    #if marginal == 'None':
        #marginal = 'Mixed Fuels'
    message.append('Current marginal fuel: {}'.format(marginal))
    message.append('Timestamp of update: {}'.format(str(last.date)))

    user_profiles = UserProfile.objects.all()
    message.append('{:d} users in database'.format(len(user_profiles)))

    names = []
    for up in user_profiles:
        user = up.userid
        if user.is_verified and user.is_active:
            names.append('{} ({})'.format(user.name, str(user.phone)))
    message.append('Active, verified users are: [{}]'.format(', '.join(names)))

    for up in user_profiles:
        user = up.userid
        if user.is_verified and user.is_active:
            ba = BALANCING_AUTHORITIES[user.state]
            if ba == 'ISONE':
                msg = up.get_personalized_message(last.fraction_green(),
                        last.fraction_high_carbon(), marginal)
                if msg is None:
                    message.append('No message sent to {}'.format(user.name))
                else:
                    message.append('To {}: "{}"'.format(user.name, msg))
                    # send_text(msg, to=user.phone)

    message = '\n'.join(message)
    print (message)
    return HttpResponse(message, "application/json")

def recurring_events(request):
    ''' Called every 5 min with a GET request'''
    # update and query BAs
    updated_bas = update_all(request)
    # Only support NE right now
    updated_bas = ['ISONE']
    newest_timepoints = [BA_MODELS[ba].objects.all().latest('date') for ba in updated_bas]
    percent_greens = [point.fraction_green() * 100.0 for point in newest_timepoints]
    percent_coals = [point.fraction_high_carbon() * 100.0 for point in newest_timepoints]
    marginal_fuels = [ne_fuels[point.marginal_fuel] for point in newest_timepoints]

    debug("ping called (marginal fuel {})".format(marginal_fuels[0]))

    #newest_timepoints = [BA_MODELS[ba].objects.all().latest('date') for ba in updated_bas]
    #percent_greens = [point.fraction_green() * 100.0 for point in newest_timepoints]
    #percent_coals = [point.fraction_high_carbon() * 100.0 for point in newest_timepoints]
    #marginal_fuels = [point.marginal_names() for point in newest_timepoints]
    #
#
    #print updated_bas, percent_greens, percent_coals, marginal_fuels

    # loop over users
    for up in UserProfile.objects.all():
        # get matching user
        user = up.userid
        debug("  looking at user {} ({}): verified? {} active? {}".format(user.name,
                str(user.phone), str(user.is_verified), str(user.is_active)))
        print user, user.is_verified, user.is_active

        # check if it's a good time
        localtime = user.local_now()
        if (user.is_verified and user.is_active and
                is_good_time_to_message(localtime, user.userid, up)):
            debug("    is verified, is active, and is good time to message")
            # get message
            ba = BALANCING_AUTHORITIES[user.state]
            if ba in updated_bas:
                ba_ind = updated_bas.index(ba)
                msg = up.get_personalized_message(percent_greens[ba_ind],
                        percent_coals[ba_ind], marginal_fuels[ba_ind])
                print user.phone, msg

                if msg:
                    if len(msg) < 150:
                        debug('      sending message!')
                        # send text
                        send_text(msg, to=user.phone)

                        # save to log
                        logitem = SMSLog(user=user,
                                         utctime=now(),
                                         localtime=localtime,
                                         message=msg)
                        logitem.save()
                    else:
                        debug('      Failed to send message "{}" as it is too long.'.format(msg))
                else:
                    debug('      active, verified user, but not right fuel now')
        else:
            debug('    either not verified, not active, or not good time to message')

    # return
    #url = reverse('home')
    #return HttpResponseRedirect(url)
    return HttpResponse('ping5 {}'.format(str(now())), "application/json")

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
    text_period_secs = SENDTEXT_TIMEDELTAS[user_profile.text_freq].total_seconds()
    if SMSLog.objects.filter(user=userid).exists():
        dt = (timestamp - SMSLog.objects.filter(user=userid).latest('utctime').localtime).total_seconds()

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
    # return bool
    # if is_good_hour and (not is_recently_notified) and is_randomly_selected:
    if is_good_hour and (not is_recently_notified):
        return True
    else:
        return False

# A dictionary
#   keys: strings (database name)
#   values: pairs of:
#       model class
#       lists of either a string (attribute name) or a pair of
#           a string (attribute name)
#           a function taking one argument (an instance of the model class) and
#               returning attribute value, or None
model_formats = {
    'User' : (accounts.models.User, [
            'name',
            'email',
            'phone',
            'verification_code',
            'is_verified',
            'is_active',
            'userid',
            'state']),
    'UserProfile' : (accounts.models.UserProfile, [
            ('userid', (lambda up : up.userid.userid)),
            'goal',
            'text_freq',
            'channel',
            'ac',
            'furnace',
            'water_heater']),
    'Debug' : (windfriendly.models.DebugMessage, [
            'date',
            'message']),
    'SMSLog' : (workers.models.SMSLog, [
            ('user', (lambda sms : sms.user.userid)),
            'utctime',
            'message']),
    'BPA'   : (windfriendly.models.BPA, [
            'load',
            'wind',
            'thermal',
            'hydro',
            'date']),
    'NE'    : (windfriendly.models.NE, [
            'gas',
            'nuclear',
            'hydro',
            'coal',
            'other_renewable',
            'other_fossil',
            'marginal_fuel',
            'date'])
        }

def data_dump_one(model, attributes):
    results = []
    for i in model.objects.all():
        value = {}
        for attribute in attributes:
            if isinstance(attribute, str):
                value[attribute] = str(getattr(i, attribute))
            else:
                if len(attribute) == 1:
                    value[attribute[0]] = str(getattr(i, attribute[0]))
                elif len(attribute) == 2:
                    value[attribute[0]] = str(attribute[1](i))
        results.append(value)
    return results

def data_dump(request, database):
    if database in model_formats:
        model, attributes = model_formats[database]
        msg = json.dumps(data_dump_one(model, attributes))
    elif database == 'all':
        result = {}
        for name in model_formats:
            model, attributes = model_formats[name]
            result[name] = data_dump_one(model, attributes)
        msg = json.dumps(result)
    else:
        msg = "Don't recognize '{}', known models are: {}".format(
                str(database),
                str(list(model_formats.keys())))
    return HttpResponse(msg, 'application/json')

def end_of_alpha_email():
    send_mail('Thanks for participating in the WattTime test',
            alpha_completed('Eric'),
            EMAIL_HOST_USER,
            ['eric.stansifer@gmail.com'])
    for user in User.objects.all():
        if user.is_active and user.is_verified:
            print ("Sending email to {} ({})".format(user.name, user.email)))
            if user.name == 'Test5':
                send_mail('Thanks for participating in the WattTime test',
                        alpha_completed(user.name),
                        EMAIL_HOST_USER,
                        [user.email])
                print ("Actually sending email now!")
