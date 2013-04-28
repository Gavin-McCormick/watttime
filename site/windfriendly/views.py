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
import json

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404

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
  end = request.GET.get('end', '')
  min =  min_date(userid)
  max = max_date(userid)
  if not start or start < min:
    start = min
  if not end or start < max:
    end = max
    
  # get user data in range
  user_rows = MeterReading.objects.filter(date__gte=start, date__lt=end, userid__exact=userid)

  # collect sums
  total_green_kwh = reduce(sum, map(used_kwh, user_rows, 'green'))
  total_kwh = reduce(sum, map(used_kwh, user_rows, 'all'))

  data = {
    'lat': lat,
    'lng': lng,
    'balancing_authority': ba,
    'time': time,
    'percent_green': round(percent_green,3)
  }
  return data
  template = 'templates/default.json'
  return render_to_response(template, RequestContext(request,{'json':data}))

def min_date(userid):
  """ Returns the earliest date with both BPA and user data """
  min_for_user = MeterReading.objects.earliest('start')
  min_for_ba = BPA.objects.earliest('date')
  return max(min_for_user, min_for_ba)

def max_date(userid):
  """ Returns the latest date with both BPA and user data """
  max_for_user = MeterReading.objects.latest('start')
  max_for_ba = BPA.objects.latest('date')
  return min(max_for_user, max_for_ba)

def utility_rows_for_user_row(user_row):
  # get utility rows for user row
  start = user_row.start
  end = user_row.start + timedelta(0,user_row.duration)
  rows = BPA.objects.filter(date__gte=start, date__lte=end)

  # get nearby values if none in range
  if rows.count() == 0:
    rows = BPA.objects.filter(date__lt=start).latest()
    if rows.count() == 0:
      rows = BPA.objects.filter(date__gt=end).earliest()

  # return
  return rows
  
def used_kwh(user_row, flag='all'):
  pass
