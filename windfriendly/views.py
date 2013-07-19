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
import logging
import numpy

from django.http import HttpResponse

from windfriendly.models import User, MeterReading, group_by_hour
from windfriendly.parsers import GreenButtonParser
from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS
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
    
def utctimes_from_request(request):
    # get requested date range, if any
    start = request.GET.get('start', None)
    end = request.GET.get('end', None)
    tz_offset = request.GET.get('tz', 0)

    # set up actual start and end times (default is -Inf to now)
    if start:
        utc_start = datetime.strptime(start, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
        utc_start += timedelta(hours = int(tz_offset))
    else:
        utc_start = datetime.min.replace(tzinfo=pytz.utc)
    if end:
        utc_end = datetime.strptime(end, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
        utc_end += timedelta(hours = int(tz_offset))
    else:
        utc_end = datetime.utcnow().replace(tzinfo=pytz.utc)
        
    return utc_start, utc_end

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
    # try to get info from request
    try:
        file = request.GET.get('file', None)
        uid = request.GET.get('uid', None)
        name = request.GET.get('name', 'New User')

    # ok if passed without request
    except:
        file = None
        uid = None
        name = None

    # update utility
    ba = utility.upper()
    if ba in BA_PARSERS:
        parser = BA_PARSERS[ba]()
    elif utility == 'gb':
        if uid is None:
            uid = User.objects.create(name=name).pk
        parser = GreenButtonParser(file, uid)
    else:
        raise ValueError("No update instructions found for %s" % utility)

    # return
    return parser.update()

@json_response
def current(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)

    # get most recent row from model
    row = BA_MODELS[ba_name].latest_point()

    # return
    return row.to_dict()

@json_response
def summarystats(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get userid
    userid = request.GET.get('id', None)

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)
        
    # raise error if no BA

    # get numbers for BA only
    if userid is None:
      # get rows
      ba_rows = BA_MODELS[ba_name].points_in_date_range(utc_start, utc_end)
      if len(ba_rows) == 0:
          raise ValueError('no data for UTC start %s, end %s' % (repr(utc_start), repr(utc_end)))

      # collect sums
      fraction_green_kw = sum([row.fraction_green() for row in ba_rows]) / len(ba_rows)
      percent_green = fraction_green_kw * 100.0

    # get numbers for user and BA data
#    else:
#        # TODO broken!!!! need to fix date handling
#        userid = int(userid)
#
#        # get user meter objects
#        meter_qset = MeterReading.objects.filter(userid__exact=userid)
#
#        # get matching dates
#        min = windutils.min_date(meter_qset, ba_qset)
#        max = windutils.max_date(meter_qset, ba_qset)
#        if starttime < min:
#          starttime = min
#        if endtime > max:
#          endtime = max
#    
#        # get user data in range
#        meter_rows = meter_qset.filter(start__gte=starttime,
#                                       start__lt=endtime)
#        if len(meter_rows) == 0:
#          raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))
#
#        # collect sums
#        total_green_kwh = sum([windutils.used_green_kwh(row, ba_qset) for row in meter_rows])
#        total_kwhs = sum([windutils.total_kwh(row, ba_qset) for row in meter_rows])
#        percent_green = total_green_kwh / total_kwhs * 100.0

    # collect data
    data = {
      'balancing_authority': ba_name,
      'userid': userid,
      'utc_start': utc_start.isoformat(),
      'utc_end': utc_end.isoformat(),
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

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)

    # get rows
    ba_rows = BA_MODELS[ba_name].points_in_date_range(utc_start, utc_end)
    if len(ba_rows) == 0:
        print 'no data for UTC start %s, end %s' % (repr(utc_start), repr(utc_end))
        return []
    
    # collect data
    data = [r.to_dict() for r in ba_rows]

    # return
    return data
    
@json_response
def averageday(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)

    # get rows
    ba_rows = BA_MODELS[ba_name].points_in_date_range(utc_start, utc_end)
    if len(ba_rows) == 0:
        print 'no data for UTC start %s, end %s' % (repr(utc_start), repr(utc_end))
        return []
    
    # collect data
    hour_groups = group_by_hour(ba_rows)
    data = []
    for hour, group in enumerate(hour_groups):
        if group is not None:
            # get average data
            average_green = round(numpy.mean([r.fraction_green() for r in group])*100, 3)
            average_dirty = round(numpy.mean([r.fraction_high_carbon() for r in group])*100, 3)
            average_load = numpy.mean([r.total_load() for r in group])
            representative_date = group.latest('date').date.replace(minute=0)
        else:
            # get null data
            average_green = None
            average_dirty = None
            average_load = None
            representative_date = BA_MODELS[ba_name].latest_date().replace(hour=hour, minute=0)
        
        # complicated date wrangling to get all local_time values in local today
        utcnow = datetime.utcnow().replace(tzinfo=pytz.utc)
        latest_day = utcnow.astimezone(BA_MODELS[ba_name].TIMEZONE).day
        local_time = representative_date.astimezone(BA_MODELS[ba_name].TIMEZONE).replace(day=latest_day)
        utc_time = local_time.astimezone(pytz.utc)
        
        # add to list
        data.append({'percent_green': average_green,
                     'percent_dirty': average_dirty,
                     'load_MW': average_load,
                     'utc_time': utc_time.strftime('%Y-%m-%d %H:%M'),
                     'local_time': local_time.strftime('%Y-%m-%d %H:%M'),
                     'hour': local_time.hour,
                    })

    # return
    return sorted(data, key=lambda r: r['local_time'])

@json_response
def today(request):
    """Get best data from today (actual until now, best forecast for future)"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get date range
    ba_local_now = datetime.now(BA_MODELS[ba_name].TIMEZONE)
    ba_local_start = ba_local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    ba_local_end = ba_local_start + timedelta(1) - timedelta(0, 1)
    utc_start = ba_local_start.astimezone(pytz.utc)
    utc_end = ba_local_end.astimezone(pytz.utc)

    # get rows
    ba_rows = BA_MODELS[ba_name].best_guess_points_in_date_range(utc_start, utc_end)
    if len(ba_rows) == 0:
        print 'no data for local start %s, end %s' % (repr(ba_local_start), repr(ba_local_end))
        return []
    
    # collect data
    data = [r.to_dict() for r in ba_rows]

    # return
    return data
    
@json_response
def greenest_subrange(request):
    """Get best beginning, end, and percent green for a sub-timeperiod"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)
    nhours = int(request.GET.get('nhours', 1))

    # get greenest subrange
    best_rows, best_timepair, best_green = BA_MODELS[ba_name].greenest_subrange(utc_start,
                                                                                utc_end,
                                                                                timedelta(hours=nhours))
    # if no data, return nulls
    if best_timepair is None:
        raise ValueError("no data found for start %s, end %s, nhours %d" % (utc_start, utc_end, nhours))
    
    # collect data
    data = {
            'percent_green' : round(best_green*100, 3),
            'utc_start' : best_timepair[0],
            'utc_end' : best_timepair[1],
            'local_start' : best_timepair[0].astimezone(BA_MODELS[ba_name].TIMEZONE),
            'local_end' : best_timepair[1].astimezone(BA_MODELS[ba_name].TIMEZONE),
            }

    # return
    return data
      
@json_response
def alerts(request):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_name is None:
        raise ValueError("No balancing authority found, check location arguments.")

    # set up actual start and end times (default is today in BA local time)
    utc_start, utc_end = utctimes_from_request(request)
    if not utc_start:
        ba_local_now = datetime.now(BA_MODELS[ba_name].TIMEZONE)
        ba_local_start = ba_local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        utc_start = ba_local_start.astimezone(pytz.utc)
    if not utc_end:
        ba_local_now = datetime.now(BA_MODELS[ba_name].TIMEZONE)
        ba_local_start = ba_local_now.replace(hour=0, minute=0, second=0, microsecond=0)
        ba_local_end = ba_local_start + timedelta(1) - timedelta(0, 1)
        utc_end = ba_local_end.astimezone(pytz.utc)

    # get best guess data
    ba_rows = BA_MODELS[ba_name].best_guess_points_in_date_range(utc_start, utc_end)
    
    # set up storage
    if len(ba_rows) > 0:
        data = {}
    else:
        return {}

    # get notable times
    sorted_green = sorted(ba_rows, key=lambda r : r.fraction_green(), reverse=True)
    data['highest_green'] = sorted_green[0].to_dict()
    sorted_dirty = sorted(ba_rows, key=lambda r : r.fraction_high_carbon(), reverse=True)
    data['highest_dirty'] = sorted_dirty[0].to_dict()
    sorted_load = sorted(ba_rows, key=lambda r : r.total_load(), reverse=True)
    data['highest_load'] = sorted_load[0].to_dict()
    data['lowest_load'] = sorted_load[-1].to_dict()
    sorted_marginal = sorted(ba_rows, key=lambda r : r.marginal_fuel)
    data['worst_marginal'] = sorted_marginal[0].to_dict()
   # data['best_marginal'] = sorted_marginal[-1].to_dict() TODO: use best non-None marginal
    
    # return
    return data

@json_response
def average_usage_for_period(request, userid):
    # TODO untested and probably broken!!! check date handling

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
  

