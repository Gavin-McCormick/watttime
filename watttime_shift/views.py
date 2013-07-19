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

from .models import ShiftRequestForm
from django.shortcuts import render
import pytz
from datetime import datetime, timedelta
from windfriendly.balancing_authorities import BA_MODELS

def shift(request):
    """ View for WattTime Shift feature """
    if request.method == 'POST': # receive form 
        form = ShiftRequestForm(request.POST)
        if form.is_valid():
            # get ShiftRequest from form
            sr = form.save(commit=False)
            sr.date_created = pytz.utc.localize(datetime.utcnow())
            if request.user.is_authenticated():
                sr.requested_by = request.user
            
            # get start and end times for requested range
            requested_timedelta = timedelta(hours=sr.usage_hours)
            requested_start = sr.date_created
            requested_end = sr.date_created + timedelta(hours=sr.time_range_hours)
            
            # get best subrange and percent green
            ba_pair = filter(lambda x: x[0]==sr.ba, sr.BA_CHOICES)
            ba_name = ba_pair[0][1]
            result = BA_MODELS[ba_name].greenest_subrange(requested_start, requested_end,
                                                          requested_timedelta)
            best_rows, best_timepair, best_green = result
            best_start_str = best_timepair[0].astimezone(BA_MODELS[ba_name].TIMEZONE).strftime("%I %p").strip('0')
            best_end_str = best_timepair[1].astimezone(BA_MODELS[ba_name].TIMEZONE).strftime("%I %p").strip('0')
            
            # actually save
            sr.recommended_start = best_timepair[0]
            sr.fraction_green = best_green
            sr.save()
            
            payload = {
                        "best_start" : best_start_str,
                        "best_end" : best_end_str,
                        "best_green" : round(best_green*100, 1),
            }
            
        else: # error
            payload = {
                        "best_start" : None,
                        "best_end" : None,
                        "best_green" : None,
                        }
            
            
    else: # display form
        form = ShiftRequestForm()
        payload = {
                    "best_start" : None,
                    "best_end" : None,
                    "best_green" : None,
        }

    # render
    print payload
    payload['form'] = form
    return render(request, "watttime_shift/shift.html", payload)
    