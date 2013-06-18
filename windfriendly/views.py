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
# Authors: Josh Livni, Sam Marcellus, Anna Schneider, Kevin Yang


from datetime import datetime, timedelta
from dateutil import tz
import pytz
import json
import time
import logging

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q

from windfriendly.models import DebugMessage, User, MeterReading
from windfriendly.parsers import BPAParser, NEParser, GreenButtonParser
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS
import windfriendly.utils as windutils

def json_response(func):
  """
  A decorator thats takes a view response and turns it
  into json. If a callback is added through GET or POST
  the response is JSONP.
  """
  def decorator(request, *args, **kwargs):
    objects = func(request, *args, **kwargs)
    if isinstance(objects, HttpResponse):
      return objects
    try:
      data = json.dumps(objects)
      if 'callback' in request.REQUEST:
        # a jsonp response!
        data = '%s(%s);' % (request.REQUEST['callback'], data)
        return HttpResponse(data, "text/javascript")
    except:
        data = json.dumps(str(objects))
    return HttpResponse(data, "application/json")
  return decorator

def ba_from_request(request):
    """
    Given a GET request with location info, return balancing authority
       name and model queryset.
    Location info can be st (state), or ba (balancing authority).
    Future support for lat+lng, zipcode, country code, etc.
    Returns tuple of (string, QuerySet)
    """
    # try BA
    ba = request.GET.get('ba', None)
    if ba:
      ba = ba.upper()
      return ba, BA_MODELS[ba].objects.all()

    # try state
    state = request.GET.get('st', None)
    if state:
      state = state.upper()
      ba = BALANCING_AUTHORITIES[state]
      return ba, BA_MODELS[ba].objects.all()

    # got nothing
    logging.debug('returning null BA')
    return None, None
      
@json_response
def green(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)

    # get most recent row from model
    row = ba_qset.latest('date')

    # get data from row
    percent_green = row.fraction_green() * 100.0
    time = row.date.strftime('%Y-%m-%d %H:%M %z')
    load = row.total_load()

    # package and return data
    data = {
      'balancing_authority': ba_name,
      'local_time': time,
      'percent_green': round(percent_green,3),
      'load_MW': round(load, 1),
    }
    return data

def debug_messages(request):
    dms = DebugMessage.objects.all()
    xs = []
    for dm in dms:
        xs.append((dm.date, dm.message))
    xs.sort()
    result = []
    for x, y in xs:
        result.append('{}: {}'.format(str(x), y))
    return HttpResponse('\n'.join(result), "application/json")

@json_response
def forecast(request):
    """ TO DO: magic number 289??"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)

    # get who knows what
    row = ba_qset.order_by('-id')[:289]

    hourly_avg = 0
    forecast = []
    for i, r in enumerate(rows):
      hourly_avg += r.fraction_green() * 100.0
      if i and not i % 12: # 5 minute intervals
        data = {
          'hour': i / 12,
          'percent_green': round(hourly_avg / 12,3)
          }
        forecast.append(data)
        hourly_avg = 0
    return {
      'forecast' : forecast,
      'balancing_authority': ba_name
      }

@json_response
def update(request, utility):
    if utility in ['bpa', 'BPA']:
        parser = BPAParser(request.GET.get('file', None))
    if utility in ['ne', 'ISONE']:
        parser = NEParser()
    if utility == 'gb':
        xml_file = request.GET.get('file', '')
        uid = request.GET.get('uid', None)
        if uid is None:
            name = request.GET.get('name', 'New User')
            uid = User.objects.create(name=name).pk
        parser = GreenButtonParser(xml_file, uid)
    return parser.update()

def update_all(request):
    bas = ['BPA', 'ISONE']
    updates = [update(request, ba) for ba in bas]
    return bas

@json_response
def summarystats(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get userid
    userid = request.GET.get('id', None)

    # get date range
    start = request.GET.get('start', None)
    if start:
      starttime = datetime.strptime(start, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
    else:
      starttime = datetime.min.replace(tzinfo=pytz.utc)
    end = request.GET.get('end', None)
    if end:
      endtime = datetime.strptime(end, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
    else:
      endtime = datetime.utcnow().replace(tzinfo=pytz.utc)

    # raise error if no BA

    # get numbers for BA only
    if userid is None:
      # get dates
      if starttime < ba_qset.order_by('date')[0].date:
        starttime = ba_qset.order_by('date')[0].date
      if endtime > ba_qset.latest('date').date:
        endtime = ba_qset.latest('date').date
     # print starttime, endtime

      # get rows
      ba_rows = ba_qset.filter(date__range=(starttime, endtime))
      if len(ba_rows) == 0:
        raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))

      # collect sums
      fraction_green_kw = sum([row.fraction_green() for row in ba_rows]) / len(ba_rows)
      percent_green = fraction_green_kw * 100.0

    # get numbers for user and BA data
    else:
        userid = int(userid)

        # get user meter objects
        meter_qset = MeterReading.objects.filter(userid__exact=userid)

        # get matching dates
        min = windutils.min_date(meter_qset, ba_qset)
        max = windutils.max_date(meter_qset, ba_qset)
        if starttime < min:
          starttime = min
        if endtime > max:
          endtime = max
    
        # get user data in range
        meter_rows = meter_qset.filter(start__gte=starttime,
                                       start__lt=endtime)
        if len(meter_rows) == 0:
          raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))

        # collect sums
        total_green_kwh = sum([windutils.used_green_kwh(row, ba_qset) for row in meter_rows])
        total_kwhs = sum([windutils.total_kwh(row, ba_qset) for row in meter_rows])
        percent_green = total_green_kwh / total_kwhs * 100.0

    # collect data
    data = {
      'balancing_authority': ba_name,
      'userid': userid,
      'start': starttime.isoformat(),
      'end': endtime.isoformat(),
      'percent_green': round(percent_green,3)
      }
    return data

@json_response
def history(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get date range
    start = request.GET.get('start', None)
    if start:
      starttime = datetime.strptime(start, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
    else:
      starttime = datetime.min.replace(tzinfo=pytz.utc)
    end = request.GET.get('end', None)
    if end:
      endtime = datetime.strptime(end, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
    else:
      endtime = datetime.utcnow().replace(tzinfo=pytz.utc)

    # get rows
    ba_rows = ba_qset.filter(date__range=(starttime, endtime))
    if len(ba_rows) == 0:
      raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))
    
    # collect sums
    data = []
    for row in ba_rows:
      data.append({
          'utc_time': row.date.strftime('%Y-%m-%d %H:%M'),
          'percent_green': round(row.fraction_green() * 100, 3),
          'marginal_fuel': row.marginal_fuel,
          'load_MW': round(row.total_load(), 1),
          })

    # return
    return data

@json_response
def today(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get date range
    utc_now = datetime.utcnow().replace(tzinfo=pytz.utc)
    starttime = utc_now.replace(hour=0, minute=0, second=0, microsecond=0)
    endtime = starttime + timedelta(1) - timedelta(0, 1)

    # get rows
    ba_rows = ba_qset.filter(date__range=(starttime, endtime))
    if len(ba_rows) == 0:
      raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))
    
    # collect sums
    data = []
    for row in ba_rows:
      data.append({
          'utc_time': row.date.strftime('%Y-%m-%d %H:%M'),
          'percent_green': round(row.fraction_green() * 100, 3),
          'marginal_fuel': row.marginal_fuel,
          'load_MW': round(row.total_load(), 1),
          })

    # return
    return data


@json_response
def average_usage_for_period(request, userid):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get grouping to return
    grouping = request.GET.get('grouping')
    groupings = grouping.split(',')

    # get time info
    start = request.GET.get('start', '')
    if start:
      starttime = datetime.strptime(start, '%Y%m%d%H%M').replace(tzinfo=tz.tzlocal())
    else:
      starttime = datetime.min.replace(tzinfo=tz.tzlocal())
    end = request.GET.get('end', '')
    if end:
      endtime = datetime.strptime(end, '%Y%m%d%H%M').replace(tzinfo=tz.tzlocal())
    else:
      endtime = datetime.utcnow().replace(tzinfo=tz.tzlocal())

    # get user data
    user_rows = MeterReading.objects.filter(start__gte=starttime,
                                            start__lt=endtime,
                                            userid__exact=userid)
    if user_rows.count() == 0:
      raise ValueError('no data')

    # set up grouping functions
    hour_bucket = lambda row : row.start.astimezone(tz.tzlocal()).hour
    if not grouping:
      bucket = lambda row : 'All'
    elif grouping == 'hour':
      bucket = hour_bucket
    elif grouping == 'month':
      bucket = lambda row : row.start.strftime('%B')
    elif grouping == 'day':
      bucket = lambda row : row.start.strftime('%A')
    elif grouping == 'weekdays':
      bucket = lambda row : 'weekends' if row.start.weekday() in [0,6] else 'weekdays'

    # put rows in buckets
    buckets = {}
    for row in user_rows:
      if bucket(row) in buckets:
        if hour_bucket(row) in buckets[bucket(row)]:
          buckets[bucket(row)][hour_bucket(row)].append(row)
        else:
          buckets[bucket(row)][hour_bucket(row)] = [row]
      else:
        buckets[bucket(row)] = {}
        buckets[bucket(row)][hour_bucket(row)] = [row]

    # collect grouped and total results
    results = {}
    total_green_kwh = 0
    total_kwhs = 0
    for key,group in buckets.iteritems():
      results[key] = {}
      for subkey, subgroup in group.iteritems():
        # compute kwh
        subgroup_green_kwh = sum([windutils.used_green_kwh(row, ba_qset) for row in subgroup])
        subgroup_total_kwh = sum([windutils.total_kwh(row, ba_qset) for row in subgroup])

        # store in results
        results[key][subkey] = {}
        results[key][subkey]['total_green_kwh'] = subgroup_green_kwh
        results[key][subkey]['total_kwhs'] = subgroup_total_kwh
        results[key][subkey]['percent_green'] = subgroup_green_kwh / subgroup_total_kwh * 100.0
        results[key][subkey]['total_cost'] = row.total_cost()

        # store in totals
        total_green_kwh += subgroup_green_kwh
        total_kwhs += subgroup_total_kwh

    # get overall percent green
    percent_green = total_green_kwh / total_kwhs * 100.0
    
    # return data
    data = {
      'userid': userid,
      'ba': ba_name,
      'percent_green': round(percent_green,3),
      'total_kwh': total_kwhs,
      'buckets': results
      }
    return data
  

