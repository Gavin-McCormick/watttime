from datetime import datetime
import urllib2
from windfriendly.models import *

def getBPA(request, latest_date=None):
  # Get the latest data
  url = 'http://transmission.bpa.gov/business/operations/wind/baltwg.txt'
  try:
    result = urllib2.urlopen(url).read()
  except urllib2.URLError, e:
    raise Exception('unable to get BPA data')
  rows = result.split('\n')[7:] # First six lines are boilerplate text
  rows = [r[:-1].split('\t') for r in rows]

  # Check to see if we have existing date; continue from there
  dates = [r[0] for r in rows]
  # Most of the time we already have most of the data
  if latest_date and latest_date in dates:
    rows = rows[dates.index(latest_bpa):]

  rs= [r for r in rows if len(r) > 1] # columns are blank if no data

  # usually would just return, but example of dumping to db
  for r in rs:
    b = BPA()
    b.date = datetime.strptime(r[0], '%m/%d/%Y %H:%M')
    b.load = int(r[1])
    b.wind = int(r[2])
    b.hydro = int(r[3])
    b.thermal = int(r[4])
    b.save()


