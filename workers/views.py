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


import json

from django.http import HttpResponse
import accounts.models
import accounts.regions
import windfriendly.models
import workers.models
import watttime_shift.models

# A dictionary
#   keys: strings (database name)
#   values: pairs of:
#       model class
#       lists of either a string (attribute name) or a pair of
#           a string (attribute name)
#           a function taking one argument (an instance of the model class) and
#               returning attribute value, or None
model_formats = {
    'UserProfile' : (accounts.models.UserProfile, [
            ('active', (lambda up : up.user.is_active)),
            'password_is_set',
            'name',
            'email',
            'phone',
            'verification_code',
            'is_verified',
            'state',
            ('equipment', (lambda up : up.get_equipment())),
            'ask_feedback',
            'beta_test']),
    'CaliforniaUserProfile' : (accounts.regions.california.user_prefs_model, [
            'message_frequency',
            'forecast_email']),
    'NewEnglandUserProfile' : (accounts.regions.newengland.user_prefs_model, [
            'message_frequency']),
    'NowhereUserProfile' : (accounts.regions.null_region.user_prefs_model, []),
    'ShiftRequest' : (watttime_shift.models.ShiftRequest, [
            'date_created',
            'requested_by',
            'usage_hours',
            'time_range_hours',
            'recommended_start',
            'recommended_fraction_green',
            'baseline_fraction_green',
            'ba']),
    'KeyValue' : (workers.models.KeyValue, [
            'key',
            'value'
            'tipo']),
    'Debug' : (workers.models.DebugMessage, [
            'date',
            'message']),
    'ScheduledTasks' : (workers.models.ScheduledTasks, [
            'date',
            'command',
            'repeat',
            'repeat_interval']),
    'DailyReport' : (workers.models.DailyReport, [
            'date',
            'message']),
    'BPA'   : (windfriendly.models.BPA, [
            'load',
            'wind',
            'thermal',
            'hydro',
            'date']),
    'CAISO' : (windfriendly.models.CAISO, [
            'load',
            'wind',
            'solar',
            'forecast_code',
            'date',
            'date_extracted']),
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

def data_text_view(request, database):
    if database in model_formats:
        model, attributes = model_formats[database]
        lines = []
        for row in data_dump_one(model, attributes):
            line = '; '.join(['{}: {}'.format(k, row[k]) for k in row])
            lines.append(line)
        msg = '\n'.join(lines)
    else:
        msg = "Don't recognize '{}', known models are: {}".format(
                str(database),
                str(list(model_formats.keys())))
    return HttpResponse(msg, 'application/json')

def data_json_view(request, database):
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
