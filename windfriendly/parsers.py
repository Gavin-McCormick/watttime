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
# Authors: Sunil Abraham, Eric Stansifer, Sam Marcellus


import dateutil.parser as dp
import requests
import StringIO
import urllib2
import zipfile
import itertools
import datetime
import pytz
import os

from dateutil.relativedelta import relativedelta

from windfriendly.models import BPA, NE, MeterReading, User, MARGINAL_FUELS

import xml.etree.ElementTree as ET

from django.core.exceptions import ObjectDoesNotExist

class UtilityParser():
    pass

class CAISOParser(UtilityParser):
    def __init__(self):
        self.CAISO_BASE_URL = 'http://oasis.caiso.com/mrtu-oasis/SingleZip'
        self.BASE_PAYLOAD = {'resultformat': '6'}
        self.TOTAL_CODE = 'SLD_FCST'
        self.CLEAN_CODE = 'SLD_REN_FCST'
        self.ACTUAL_CODE = 'ACTUAL'
        self.FRCST_CODE = 'DAM'
        self.DEVIATE_CODE = 'HASP'
        self.DATE_FRMT = '%Y%m%d'

    def CSVtoRows(s):
        # poor string->list of lists. should use real CSV parsing
        # library. import csv was giving me problems...
        # file ends on \n, so skipping last (empty) row
        return [y.split(',') for y in x.split('\n')][:-1]

    def RowstoDicts(rows):
        header = rows[0]
        return [dict(zip(header, row)) for row in rows[1:]]

    def getData(self, energy_type, forecast_type, start_date, end_date):
        # returns list of dicts
        payload_update = {'queryname': energy_type,
                          'market_run_id': forecast_type,
                          'startdate': start_date, 'enddate': end_date}
        payload = dict(self.BASE_PAYLOAD.items() + payload_update)
        try: 
            r = requests.get(self.CAISO_BASE_URL, payload) # have request
        except requests.exceptions.RequestException, e:
            raise Exception('unable to get CAISO data' + str(e))
        z = zipfile.ZipFile(StringIO.StringIO(r.content)) # have zipfile
        f = z.read(z.namelist()[0]) # have csv
        return self.RowstoDicts(self.CSVtoRows(f))

    def getEnergySubsetAndCast(self, data):
        energy_keys = filter(lambda x: x[:2] == 'HE', data.keys())
        subset = dict((k, float(data[k])) for k in energy_keys)
        return subset

    def aggData(self, data):
        # take in output of getData, return dict of agged
        energy_subsets = map(self.getEnergySubsetAndCast, data)
        agged = dict([(k, reduce(lambda x, y: x.get(k, 0) + y.get(k, 0), energy_subsets))
                      for k in energy_subsets])
        return agged

    def getRatio(self, clean_energy, total_energy):
        # clean, total energy params are dicts
        ratio = dict([(k, clean_energy[k] / total_energy[k])
                 for k in clean_energy.keys()])
        return ratio

    def getDataAndAgg(self, energy_type, forecast_type, start_date, end_date):
        data = self.getData(energy_type, forecast_type, start_date, end_date)
        agged = self.aggData(data)
        return agged

    def getForecastTypeRatio(self, forecast_type, start_date, end_date):
        total_agged = getDataAndAgg(self.TOTAL_CODE, forecast_type, start_date,
                                    end_date)
        clean_agged = getDataAndAgg(self.CLEAN_CODE, forecast_type, start_date,
                                    end_date)
        agged_dict = self.getRatio(clean_agged, total_agged)
        agged_arr = [agged_dict[k] for k in sorted(agged_dict.keys())][:-1]
        # weird HE25 col has no data... so dropping last entry
        return agged_arr

    def getLatestExistingDate(self):
        latest = CAISO.objects.all().order_by('-date')
        if latest:
            return latest.date
    
    def getToday(self):
        return datetime.date.today()

    def getTomorrow(self):
        return self.getToday() + datetime.timedelta(1)

    def getCurrentHour(self):
        return datetime.datetime.now().hour
    
    def getCAISOForecast(self):
        # returns in-order array of forecast ratios
        today = self.getToday().strftime(self.DATE_FRMT)
        tomorrow = self.getTomorrow().strftime(self.DATE_FRMT)
        forecast_today = self.getForecastTypeRatio(self.FRCST_CODE, today,
                                                   today)
        forecast_tomorrow = self.getForecastTypeRatio(self.FRCST_CODE, tomorrow,
                                                 tomorrow)
        forecast_total = forecast_today + forecast_tomorrow
        current_hour = self.getCurrentHour()
        # return all future predictions -- if it's 12:30 am, return
        # predictions for 1 am and onward
        return forecast_total[current_hour + 1:]

    def dateGen(self, start_date, end_date):
        while start_date < end_date:
            yield start_date
            start_date = start_date + datetime.timedelta(1)
    
    def getCAISOHistory(self, latest=None):
        # returns history as in-order array of ratios, starting with
        # 'latest' date.
        # at march 13, 2013, historical data goes back to january
        # 2009, so if latest date not specified, grab previous 4 years
        if not latest:
            latest = getToday() - datetime.timedelta(365 * 4)
        forecast_total = []
        for d in dateGen():
            forecast = self.getForecastTypeRatio(self.FRCST_CODE, d, d)
            forecast_total.append(forecast)
        return forecast

class BPAParser(UtilityParser):
    def __init__(self, url = None):

        self.BPA_LOAD_URL = url or 'http://transmission.bpa.gov/business/operations/wind/baltwg.txt'
        #If we're pulling historical data, ignore latest
        if url is None:
            self.update_latest = True
        else:
            self.update_latest = False
        self.BPA_LOAD_NCOLS = 5
        self.BPA_LOAD_SKIP_LINES = 7

        self.BPA_OVERSUPPLY_URL = 'http://transmission.bpa.gov/business/operations/wind/twndbspt.txt'
        self.BPA_OVERSUPPLY_NCOLS = 4
        self.BPA_OVERSUPPLY_SKIP_LINES = 11

    def getData(self, url):
        # Make request for data
        try:
            data = requests.get(url).text
        except requests.exceptions.RequestException, e:
            data = urllib2.urlopen(url).read()
            #raise Exception('unable to get BPA data' + str(e))
        return data

    def parseDate(self, datestring):
        tzd = {
            'PST': -28800,
            'PDT': -25200,
        }
        tz = pytz.timezone('US/Pacific')
        dt = dp.parse(datestring, tzinfos=tzd)
        if dt.tzinfo == None:
            dt = dt.replace(tzinfo = tz)
        dt = dt.astimezone(pytz.UTC)
        return dt

    def getLatestExistingDate(self):
        latest = BPA.objects.all().order_by('-date')
        if latest:
          return latest[0].date

    def parseLoadRow(self, row):
        fields = row.split('\t')
        res = {'date': self.parseDate(fields[0])}
        if len(fields) == 5:
            try:
                [total, wind, hydro, thermal]  = [int(x) for x in fields[1:]]
            except:
                return res
            res.update({'wind': wind, 'hydro': hydro, 'thermal': thermal,
                        'total': total})
            return res
        else:
            return res

    def parseOversupplyRow(self, row):
        fields = row.split('\t')
        res = {'date': self.parseDate(fields[0])}
        if len(fields) == 4:
            [basepoint, wind, oversupply] = [int(x) for x in fields[1:]]
            res.update({'basepoint': basepoint, 'wind': wind,
                        'oversupply': oversupply})
            return res
        else:
            return res

    def rowIsAfterDate(self, row, date):
        row_date = row['date']
        return row_date > date

    def rowHasAllCols(self, row, ncols):
        return len(row) == ncols

    def isGoodRow(self, row, ncols, date=None):
        if date:
            return (self.rowHasAllCols(row, ncols) and self.rowIsAfterDate(row, date))
        else:
            return self.rowHasAllCols(row, ncols)

    def parse(self, url, parse_row_fn, skip_lines, ncols, latest_date=None):
        data = self.getData(url)
        # First skip_lines lines are boilerplate text, last line is blank
        rows = data.split('\r\n')[skip_lines:-1]
        parsed_rows = [parse_row_fn(row) for row in rows]
        res = filter(lambda x: self.isGoodRow(x, ncols, latest_date), parsed_rows)
        return res

    def parseBPALoad(self, latest_date=None):
        return self.parse(self.BPA_LOAD_URL, self.parseLoadRow,
                     self.BPA_LOAD_SKIP_LINES, self.BPA_LOAD_NCOLS,
                     latest_date)

    def parseBPAOversupply(self, latest_date=None):
        return self.parse(self.BPA_OVERSUPPLY_URL, self.parseOversupplyRow,
                     self.BPA_OVERSUPPLY_SKIP_LINES, self.BPA_OVERSUPPLY_NCOLS,
                     latest_date)

    def zipTables(self, table_a, table_b):
        max_index = reduce(min, map(len, [table_a, table_b]))
        res = []
        for i in xrange(max_index):
            res.append(dict(table_a[i].items() + table_b[i].items()))
        return res

    def getBPA(self, latest_date=None):
        parsed_load = self.parseBPALoad(latest_date)
        return parsed_load

    def writeBPA(self, row):
        b = BPA()
        b.date = row['date']
        b.load = row['total']
        b.wind = row['wind']
        b.hydro = row['hydro']
        b.thermal = row['thermal']
        b.save()

    def update(self):
        latest_date = self.getLatestExistingDate() if self.update_latest else None
        update = self.getBPA (latest_date)
        for row in update:
            self.writeBPA(row)
        if self.update_latest:
            if len(update) > 0:
                row = update[len(update)-1]
                pct_green = (row['wind'] + row['hydro']) / float(row['wind'] + row['hydro'] + row['thermal'])
            else:
                pct_green = .9
            if pct_green > .9:
                #send_text('Hey! Energy is super clean right now.  Perfect time to do the laundry or something.')
                pass
            else:
                #send_text('Hey! Dirty energy alert.  Think twice before using unnecessary energy for the next 30 min.')
                pass
        return {
          'prior_latest_date' : str(latest_date),
          'update_rows' : len(update),
          'latest_date' : str(self.getLatestExistingDate())
        }


# This was written to imitate the BPA Parser somewhat
class NEParser(UtilityParser):
    def __init__(self, request_method = None):
        if request_method is None:
            url = 'http://isoexpress.iso-ne.com/ws/wsclient'
            payload = {'_ns0_requestType':'url', '_ns0_requestUrl':'/genfuelmix/current'}
            def wrapper():
                return requests.post(url, data = payload).json()
            self.request_method = wrapper
        else:
            self.request_method = request_method

    def update(self):
        try:
            json = self.request_method()[0]['data']['GenFuelMixes']['GenFuelMix']

            timestamp = None
            ne = NE()
            ne.gas = 0
            ne.nuclear = 0
            ne.hydro = 0
            ne.coal = 0
            ne.other_renewable = 0
            ne.other_fossil = 0

            marginal_fuel = len(MARGINAL_FUELS) - 1

            for i in json:
                if timestamp is None:
                    timestamp = i['BeginDate']

                fuel = i['FuelCategory']
                gen = i['GenMw']

                if fuel == 'Natural Gas':
                    ne.gas += gen
                elif fuel == 'Nuclear':
                    ne.nuclear += gen
                elif fuel == 'Hydro':
                    ne.hydro += gen
                elif fuel == 'Coal':
                    ne.coal += gen
                # I don't really know how I should be placing some of these fuels
                elif fuel == 'Oil' or fuel == 'Landfill Gas' or fuel == 'Refuse':
                    ne.other_fossil += gen
                elif fuel == 'Wind' or fuel == 'Wood':
                    ne.other_renewable += gen
                else: # Unrecognized fuel
                    ne.other_fossil += gen

                if i['MarginalFlag'] == 'Y':
                    if fuel in MARGINAL_FUELS:
                        marginal_fuel = min(marginal_fuel, MARGINAL_FUELS.index(fuel))

            ne.marginal_fuel = marginal_fuel

            if timestamp is None:
                ne.date = None # Is this okay? Don't know.
            else:
                ne.date = dp.parse(timestamp)

            ne.save()

        except requests.exceptions.RequestException: # failed to get data
            pass
        except KeyError: # malformed json format
            pass
        except IndexError: # malformed json format
            pass
        except ValueError: # failed to parse time
            pass

        return {}

class UserDataParser:
    pass

class GreenButtonParser(UserDataParser):
    def __init__(self, xml_file, uid):
        self.uid = uid
        self.tree = ET.parse(urllib2.urlopen(xml_file))
        #self.ns = '{http://www.w3.org/2005/Atom}'
        self.ns ='{http://naesb.org/espi}'

    def parse(self):
        root = self.tree.getroot()
        for reading in root.iter(self.ns+'IntervalReading'):
            cost = reading.find(self.ns+'cost').text
            value = float(reading.find(self.ns+'value').text)/1000
            start = float(reading.find(self.ns+'timePeriod').find(self.ns+'start').text)
            start = datetime.datetime.fromtimestamp(start, pytz.UTC)
            duration = reading.find(self.ns+'timePeriod').find(self.ns+'duration').text

            yield {'cost':cost, 'value':value, 'start':start, 'duration':duration}
        

    def update(self):
        try:
            user = User.objects.get(pk = self.uid)
        except ObjectDoesNotExist: 
            print 'creating user'
            user = User.objects.create(name='New User')


        counter = 0
        for row in self.parse():
            existing = MeterReading.objects.filter(start = row['start'], userid=user)
            if existing.count() > 0:
                r = existing[0]
                if r.energy != row['value']:
                    r.energy = row['value']
                else:
                    continue
            else:
                r = MeterReading()
                r.userid = user
                r.cost = row['cost']
                r.energy = row['value']
                r.start = row['start']
                r.duration = row['duration']
            r.save()
            counter += 1
        return  {'added_count': counter, 'uid':self.uid}
