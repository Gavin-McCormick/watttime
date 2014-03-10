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
import pandas as pd

from django.contrib.syndication.views import Feed
from django.http import HttpResponse

from windfriendly.models import User, MeterReading
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

def ba_from_request(request, ba=None):
    """
    Given a GET request with location info, return balancing authority
       name and model queryset.
    Location info can be st (state), or ba (balancing authority).
    Future support for lat+lng, zipcode, country code, etc.
    Returns tuple of (string, QuerySet)
    """
    if ba:
        # use supplied ba
        ba = ba.upper()
        
    else:
        # try state
        state = request.GET.get('st', None)
        if state:
          state = state.upper()
          ba = BALANCING_AUTHORITIES.get(state, None)
    
        # try BA
        else:
            ba = request.GET.get('ba', None)
            if ba:
              ba = ba.upper()
      
    # got nothing
    try:
        return ba, BA_MODELS[ba].objects.all()
    except:
        logging.debug('returning null BA')
        return ba, None

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

    # get thing to update
    ba = utility.upper()
    if ba in BA_PARSERS:
        parser = BA_PARSERS[ba]()
    elif utility == 'gb':
        if uid is None:
            uid = User.objects.create(name=name).pk
        parser = GreenButtonParser(file, uid)
    else:
        return {"error_message": "No update instructions found for %s" % utility,
                "error_code": 2}

    # update
    try:
        result = parser.update()
        return result
    except Exception as e:
        return {"error_message": "Update failed with error: %s" % e,
                "error_code": 3}
        

@json_response
def averageday(request, ba=None):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request, ba)
    # if no BA, error
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)

    return BA_MODELS[ba_name].objects.average_day(utc_start, utc_end, BA_MODELS[ba_name].TIMEZONE)
    
@json_response
def greenest_subrange(request, ba=None):
    """Get cleanest subrange using objects.greenest_subrange"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}
        
    # get other args from request
    time_range_hours = float(request.GET.get('time_range_hours', 0))
    if not time_range_hours > 0:
        return {"error_message": "Missing or bad argument: time_range_hours (got %s)" % time_range_hours,
                "error_code": 1}
    usage_hours = float(request.GET.get('usage_hours', 0))
    if not usage_hours > 0:
        return {"error_message": "Missing or bad argument: usage_hours (got %s)" % usage_hours,
                "error_code": 1}
    elif usage_hours > time_range_hours:
        return {"error_message": "Bad arguments: usage_hours %s should be < time_range_hours %s" % (usage_hours, time_range_hours),
                "error_code": 1}

    # calculate result
    date_created = datetime.now(BA_MODELS[ba_name].TIMEZONE).astimezone(pytz.utc)
    requested_end = date_created + timedelta(hours=time_range_hours)
    requested_timedelta = timedelta(hours=usage_hours)
    result = BA_MODELS[ba_name].objects.greenest_subrange(date_created, requested_end,
                                                          requested_timedelta)
    best_rows, best_timepair, best_green, baseline_green = result

    # return
    if best_timepair:
        return {"recommended_start": best_timepair[0].strftime('%Y-%m-%d %H:%M'),
                "recommended_end": best_timepair[1].strftime('%Y-%m-%d %H:%M'),
                "recommended_fraction_green": best_green,
                "baseline_fraction_green": baseline_green,
                "date_created": date_created.strftime('%Y-%m-%d %H:%M'),
                "recommended_local_start": best_timepair[0].astimezone(BA_MODELS[ba_name].TIMEZONE).strftime('%Y-%m-%d %H:%M'),
                "recommended_local_end": best_timepair[1].astimezone(BA_MODELS[ba_name].TIMEZONE).strftime('%Y-%m-%d %H:%M'),
                }
    else:
        return {"error_message": "Something went wrong with start %s, end %s, delta %s" % (date_created, requested_end, requested_timedelta),
                "error_code": 3}
        
@json_response
def today(request, ba=None):
    """Get best data from today (actual until now, best forecast for future)"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}

    # get date range
    ba_local_now = datetime.now(BA_MODELS[ba_name].TIMEZONE)
    ba_local_start = ba_local_now.replace(hour=0, minute=0, second=0, microsecond=0)
    ba_local_end = ba_local_start + timedelta(1) - timedelta(0, 1)
    utc_start = ba_local_start.astimezone(pytz.utc)
    utc_end = ba_local_end.astimezone(pytz.utc)

    # get rows
    ba_rows = ba_qset.filter(date__range=(utc_start, utc_end)).best_guess_points()
    if len(ba_rows) == 0:
        print 'no data for local start %s, end %s' % (repr(ba_local_start), repr(ba_local_end))
        return []
    rows_on_day = []
    for row in ba_rows:
        if row.local_date.day == ba_local_now.day:
            rows_on_day.append(row)

    # collect data
    data = [r.to_dict() for r in rows_on_day]

    # return
    return data

@json_response
def history_hourly(request, ba=None):
    """Get hourly average history data"""
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}

    # get requested date range
    utc_start, utc_end = utctimes_from_request(request)

    # return
    return BA_MODELS[ba_name].objects.rollup(utc_start, utc_end, BA_MODELS[ba_name].TIMEZONE, how='hourly')

@json_response
def alerts(request, ba=None):
    # get name and queryset for BA
    ba_name, ba_qset = ba_from_request(request)
    # if no BA, error
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}

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
    ba_rows = ba_qset.filter(date__range=(utc_start, utc_end)).best_guess_points()
    # set up storage
    if len(ba_rows) > 0:
        data = {}
    else:
        return {}

    # get notable times
    sorted_green = sorted(ba_rows, key=lambda r : r.fraction_clean, reverse=True)
    data['highest_green'] = sorted_green[0].to_dict()
    sorted_gen = sorted(ba_rows, key=lambda r : r.total_MW, reverse=True)
    data['highest_gen'] = sorted_gen[0].to_dict()
    data['lowest_gen'] = sorted_gen[-1].to_dict()
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
    if ba_qset is None:
        return {"error_message": "Missing or bad argument: ba or st (got %s)" % ba_name,
                "error_code": 1}

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
      return []

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
      "userid": userid,
      "ba": ba_name,
      "percent_green": round(percent_green,3),
      "total_kwh": total_kwhs,
      "buckets": results
      }
    return data

_epoch = datetime(2000, 1, 1, tzinfo = pytz.utc)


class ToggleFeed(Feed):
    title = "Toggle every hour feed"
    link = "/"
    description = "Alternatively yields O N or O F F every hour."

    def items(self):
        now = datetime.now(pytz.utc)
        last = now.replace(minute = 0, second = 0, microsecond = 0)
        on = (last.hour % 2 == 0)

        xs = []
        for i in range(5):
            xs.append((last, on))
            on = not on
            last = last - timedelta(hours = 1)

        return xs

    def item_title(self, item):
        if item[1]:
            return "turn on"
        else:
            return "turn off"

    def item_description(self, item):
        if item[1]:
            return "turn thing on"
        else:
            return "turn thing off"

    def item_guid(self, item):
        return int((item[0] - _epoch).total_seconds())

    def item_pubdate(self, item):
        return item[0]

    def item_link(self, item):
        return '/'
