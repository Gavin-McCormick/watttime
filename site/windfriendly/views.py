# Copyright 2013 Google Inc.
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
# Author: Josh Livni (jlivni@google.com)


from datetime import datetime, timedelta
import pytz
import json
import time

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404
from django.db.models import Q

from windfriendly.models import BPA, Normalized, User, MeterReading
from windfriendly.parsers import BPAParser, GreenButtonParser

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


def getBalancingAuthority(lat, lng):
  return 'BPA'

def total_load(row):
  """ Returns the total load """
  return float(row.wind + row.hydro + row.thermal)

def fraction_wind(row):
  """ Returns the fraction of the total load from wind """
  return (row.wind) / float(row.wind + row.hydro + row.thermal)

def fraction_hydro(row):
  """ Returns the fraction of the total load from hydro """
  return (row.hydro) / float(row.wind + row.hydro + row.thermal)

def fraction_fossil(row):
  """ Returns the fraction of the total load from fossil fuels (ie thermal) """
  return (row.thermal) / float(row.wind + row.hydro + row.thermal)

def fraction_nonfossil(row):
  """ Returns the fraction of the total load from anything besides fossil fuels (ie wind+hydro) """
  return (row.wind + row.hydro) / float(row.wind + row.hydro + row.thermal)

@json_response
def status(request):
  lat = request.GET.get('lat', '')
  lng = request.GET.get('lng', '')

  ba = getBalancingAuthority(lat, lng)
  row = BPA.objects.latest('date')

  percent_green = fraction_wind(row) * 100.0
  time = row.date.strftime('%Y-%m-%d %H:%M')

  data = {
    'lat': lat,
    'lng': lng,
    'balancing_authority': 'BPA',
    'time': time,
    'percent_green': round(percent_green,3)
  }
  return data
  template = 'templates/default.json'
  return render_to_response(template, RequestContext(request,{'json':data}))

@json_response
def forecast(request):
  lat = request.GET.get('lat', '')
  lng = request.GET.get('lng', '')

  rows = BPA.objects.all().order_by('-id')[:289]
  hourly_avg = 0
  forecast = []
  for i, r in enumerate(rows):
    hourly_avg += fraction_wind(r) * 100.0
    if i and not i % 12: # 5 minute intervals
      data = {
        'hour': i / 12,
        'percent_green': round(hourly_avg / 12,3)
      }
      forecast.append(data)
      hourly_avg = 0
  return {
    'forecast' : forecast,
    'balancing_authority': 'BPA'
  }

@json_response
def update(request, utility):
  if utility == 'bpa':
    parser = BPAParser(request.GET.get('file', 'http://transmission.bpa.gov/business/operations/wind/baltwg.txt'))
  if utility == 'gb':
    xml_file = request.GET.get('file', '')
    uid = request.GET.get('uid', None)
    if uid is None:
        name = request.GET.get('name', 'New User')
        uid = User.objects.create(name=name).pk

    parser = GreenButtonParser(xml_file, uid)
  return parser.update()

@json_response
def history(request, userid):
  # get balancing authority
  lat = request.GET.get('lat', '')
  lng = request.GET.get('lng', '')
  ba = getBalancingAuthority(lat, lng)

  # get date range
  start = request.GET.get('start', '')
  if start:
    starttime = datetime.strptime(start, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
  else:
    starttime = datetime.min.replace(tzinfo=pytz.utc)
  end = request.GET.get('end', '')
  if end:
    endtime = datetime.strptime(end, '%Y%m%d%H%M').replace(tzinfo=pytz.utc)
  else:
    endtime = datetime.utcnow().replace(tzinfo=pytz.utc)
  print starttime, endtime

  # get numbers for BPA
  if userid == 'bpa':
    # get dates
    if starttime < BPA.objects.order_by('date')[0].date:
      starttime = BPA.objects.order_by('date')[0].date
    if endtime > BPA.objects.latest('date').date:
      endtime = BPA.objects.latest('date').date
    print starttime, endtime

    # get rows
    utility_rows = BPA.objects.filter(date__range=(starttime, endtime))
    if len(utility_rows) == 0:
      raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))

    # collect sums
    fraction_green_kw = reduce(lambda x, y: x+y,
                            map(fraction_nonfossil, utility_rows)) / len(utility_rows)
    percent_green = fraction_green_kw * 100.0

  # get numbers for user
  else:
    userid = int(userid)
    # get dates
    min = min_date(userid)
    max = max_date(userid)
    if starttime < min:
      starttime = min
    if endtime > max:
      endtime = max
    
    # get user data in range
    user_rows = MeterReading.objects.filter(start__gte=starttime,
                                            start__lt=endtime,
                                            userid__exact=userid)
    if len(user_rows) == 0:
      raise ValueError('no data for start %s, end %s' % (repr(starttime), repr(endtime)))

    # collect sums
    total_green_kwh = reduce(lambda x, y: x+y,
                             [used_kwh(row, 'green') for row in user_rows])
    total_kwh = reduce(lambda x, y: x+y,
                       map(used_kwh, user_rows))
    print total_green_kwh, total_kwh
    percent_green = total_green_kwh / total_kwh * 100.0

  # collect data
  data = {
    'lat': lat,
    'lng': lng,
    'balancing_authority': ba,
    'userid': userid,
    'start': starttime.isoformat(),
    'end': endtime.isoformat(),
    'percent_green': round(percent_green,3)
  }
  return data
  template = 'templates/default.json'
  return render_to_response(template, RequestContext(request,{'json':data}))

def test_q(request, userid):
  # get user data
  user_rows = MeterReading.objects.filter(userid__exact=int(userid))
  print len(user_rows.filter(Q(start__day=2)))
  print len(user_rows.filter(Q(start__day=3)))
  print len(user_rows.filter(Q(start__day=2) | Q(start__day=3)))
 

def average_usage_for_hours(request, userid):
  # hack!!
  utchack = 7

  # get balancing authority
  lat = request.GET.get('lat', '')
  lng = request.GET.get('lng', '')
  ba = getBalancingAuthority(lat, lng)

  # get time info
  month = request.GET.get('month', None)
  days = request.GET.get('days', 'all').strip()
  print days, month

  # get user data
  user_rows = MeterReading.objects.filter(userid__exact=int(userid))
  if month is not None:
    user_rows = user_rows.filter(start__month=int(month))
  else:
    month = 'all'
  if days == 'weekdays':
    user_rows = user_rows.filter(Q(start__day=2) | Q(start__day=3) |
                                 Q(start__day=4) | Q(start__day=5) | Q(start__day=6))
  elif days == 'weekends':
    user_rows = user_rows.filter(Q(start__day=1) | Q(start__day=7))
      
  print len(user_rows)
  if len(user_rows) == 0:
    raise ValueError('no data for days=%s, month=%s' % (days, month))
  
  # set up storage for sums and counts
  sum_percent_green = [0 for i in range(24)]
  sum_kw = [0 for i in range(24)]
  sum_cost_per_hour = [0 for i in range(24)]
  counts = [0 for i in range(24)]

  # collect averages
  t0 = time.clock()
  for row in user_rows:
    total_green_kwhs = used_kwh(row, 'green')
    total_kwhs = total_kwh(row)
    sum_percent_green[row.start.hour] += total_green_kwhs / total_kwhs * 100.0
    sum_kw[row.start.hour] += total_kwhs * row.duration / 1000.0
    sum_cost_per_hour[row.start.hour] += row.cost * row.duration / 3600.0 / 10000.0
    counts[row.start.hour] += 1
  t1 = time.clock()
  print t1-t0
  percent_greens = [float(sum_percent_green[i])/max(1.0, counts[i]) for i in range(24)]
  av_kw = [float(sum_kw[i])/max(1.0, counts[i]) for i in range(24)]
  av_cost = [float(sum_cost_per_hour[i])/max(1.0, counts[i]) for i in range(24)]

  # collect data
  data = {
    'lat': lat,
    'lng': lng,
    'balancing_authority': ba,
    'userid': userid,
    'av_percent_greens': [percent_greens[i%24] for i in range(utchack, 24+utchack)],
    'month': month,
    'days': days,
    'av_kw': [av_kw[i%24] for i in range(utchack, 24+utchack)],
    'av_cost': [av_cost[i%24] for i in range(utchack, 24+utchack)]
  }
  print data
  template = 'templates/default.json'
  return render_to_response(template, RequestContext(request,{'json':data}))
  

def min_date(userid):
  """ Returns the earliest date with both BPA and user data """
  min_for_user = MeterReading.objects.order_by('start')[0].start
  min_for_ba = BPA.objects.order_by('date')[0].date
  return max(min_for_user, min_for_ba)

def max_date(userid):
  """ Returns the latest date with both BPA and user data """
  max_for_user = MeterReading.objects.latest('start').start
  max_for_ba = BPA.objects.latest('date').date
  return min(max_for_user, max_for_ba)

def utility_rows_for_user_row(user_row):
  # get utility rows for user row
  start = user_row.start
  end = user_row.start + timedelta(0,user_row.duration)
  rows = BPA.objects.filter(date__range=(start, end))

  # get nearby values if none in range
#  if rows.count() == 0:
#    print start, end
#    rows = BPA.objects.filter(date__lt=start).latest('date')
#    if len(rows) == 0:
#      rows = [BPA.objects.filter(date__gt=end).order_by('date')[0]]

  # return
  return rows
  
def used_kwh(user_row, flag=None):
  utility_rows = utility_rows_for_user_row(user_row)
  try:
    n_rows = float(len(utility_rows))
  except:
    return 0.0

  if flag=='green':
    try:
      fraction_load = sum([fraction_nonfossil(row) for row in utility_rows]) / n_rows
    except ZeroDivisionError:
      return 0.0
  else:
    fraction_load = 1.0

  return total_kwh(user_row) * fraction_load

def total_kwh(user_row):
  kwh = user_row.energy/3600.0 * user_row.duration
  return kwh
