from datetime import datetime
import json

from django.conf import settings
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.http import HttpResponse, HttpResponseRedirect, HttpResponseForbidden, Http404

from windfriendly.models import BPA, Normalized


def home(request):
  return render_to_response('templates/index.html', RequestContext(request,{}))

def getBalancingAuthority(lat, lng):
  return 'bpa'

def status(request):
  lat = request.GET.get('lat', '')
  lng = request.GET.get('lng', '')

  ba = getBalancingAuthority(lat, lng)
  raw = BPA.objects.latest('date')

  percent_green = raw.wind * 1.0 / (raw.wind + raw.hydro + raw.thermal)
  time = datetime.now().strftime('%Y-%m-%d %H:%M')

  data = {
    'lat': lat,
    'lng': lng,
    'balancing_authority': 'BPA',
    'time': time,
    'percent_green': percent_green
  }
  data = json.dumps(data)
  template = 'templates/default.json'
  return render_to_response(template, RequestContext(request,{'json':data}))


def details(request):
  return
