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
# Authors: Anna Schneider, Eric Stansifer


from windfriendly.models import MARGINAL_FUELS, debug
from windfriendly.views import update
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS
from accounts.twilio_utils import send_text
from accounts.models import UserProfile
from django.http import HttpResponse
from django.utils.timezone import now
from workers.models import SMSLog
from workers.tasks import run_frequent_tasks, run_hourly_tasks

def demo(request):
    message = []

    update(request, 'ne')
    message.append('Updated latest New England data.')

    last = BA_MODELS['ISONE'].latest_point()
    message.append('Natural Gas: {:.2f} MW'.format(last.gas))
    message.append('Nuclear: {:.2f} MW'.format(last.nuclear))
    message.append('Hydro: {:.2f} MW'.format(last.hydro))
    message.append('Coal: {:.2f} MW'.format(last.coal))
    message.append('Other renewable fuels: {:.2f} MW'.format(last.other_renewable))
    message.append('Other fossil fuels: {:.2f} MW'.format(last.other_fossil))
    marginal = MARGINAL_FUELS[last.marginal_fuel]
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
    debug('recurring_events called at {}'.format(str(now())))
    run_frequent_tasks()
    run_hourly_tasks()
    return HttpResponse('ping5 {}'.format(str(now())), "application/json")
