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

from django.test import TestCase
import pytz
from datetime import datetime, timedelta

from windfriendly.balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS

class BAInfoTestCase(TestCase):
    """Test contents of balancing_authorities.py"""

    def test_supported_states(self):
        for st in ['CA',
                   'CT', 'MA', 'ME', 'NH', 'RI', 'VT', 
                   'ID', 'OR', 'WA',
                   'MN', 'MI', 'IA', 'IL', 'IN', 'ND', 'SD', 'WI',
                   'PA', 'NJ', 'MD', 'DE', 'DC', 'VA', 'WV', 'KY']:
            self.assertIn(st, BALANCING_AUTHORITIES.keys())

    def test_supported_bas(self):
        for ba in ['BPA', 'ISONE', 'CAISO', 'MISO', 'PJM']:
            self.assertIn(ba, BA_MODELS.keys())
            self.assertIn(ba, BA_PARSERS.keys())


class BaseBATestCase(object):
    """Test generic model"""
    maxDiff = None

    def test_fractions(self):
        row = self.model.objects.get(pk=1)
        self.assertLess(row.fraction_clean, 1)
        self.assertGreaterEqual(row.fraction_clean, 0)

    def test_latest(self):
        self.assertEqual(self.model.objects.all().latest().date,
                         max(self.model.objects.all(), key=lambda r: r.date).date)
        self.assertEqual(self.model.objects.all().earliest().date,
                         min(self.model.objects.all(), key=lambda r: r.date).date)

    def test_points_in_date_range(self):
        rows = self.model.objects.filter(date__range=(self.start, self.end))
        self.assertGreater(rows.count(), 0)
        for ir, r in enumerate(rows):
            # test in range
            self.assertGreaterEqual(r.date, self.start)
            self.assertLessEqual(r.date, self.end)

            # test sorted
            # requires monotonically increasing dates, but tolerates non-unique dates
            if ir > 0:
                self.assertGreaterEqual(r.date, rows[ir-1].date)

    def test_points_in_date_range_empty(self):
        rows = self.model.objects.filter(date__range=(self.bad_start, self.bad_end))

        # should be empty queryset
        self.assertEqual(rows.count(), 0)

    def test_points_in_date_range_bad_dates(self):
        rows = self.model.objects.filter(date__range=(self.end, self.start))

        # should be empty queryset
        self.assertEqual(rows.count(), 0)

    def test_best_guess(self):
        r_by_pk = self.model.objects.get(pk=1)
        r_by_date = self.model.objects.all().filter(date=r_by_pk.date).best_guess()
        self.assertEqual(r_by_date, r_by_pk)

    def test_greenest_subrange(self):
        td = timedelta(0, 2)
        result = self.model.objects.greenest_subrange(self.start, self.end, td)
        rows, timepair, best_green, baseline_green = result
        self.assertEqual(timepair[1] - timepair[0], td)
        self.assertGreater(best_green, baseline_green)
        self.assertGreater(len(rows), 0)

    def test_greenest_subrange_error(self):
        td = self.end - self.start + timedelta(0, 1)
        result = self.model.objects.greenest_subrange(self.start, self.end, td)
        rows, timepair, best_green, baseline_green = result
        self.assertIsNone(rows)
        self.assertIsNone(timepair)
        self.assertEqual(best_green, 0)
        self.assertGreater(baseline_green, 0)


class BPATestCase(BaseBATestCase, TestCase):
    """Test BPA model"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class

    fixtures = ['bpa.json']
    model = BA_MODELS['BPA']
    start = datetime(2013, 11, 28, tzinfo=pytz.utc)
    end = datetime(2013, 11, 29, tzinfo=pytz.utc)
    bad_start = datetime(2013, 05, 01, tzinfo=pytz.utc)
    bad_end = datetime(2013, 05, 30, tzinfo=pytz.utc)

    def test_data_available(self):
        self.assertGreater(self.model.objects.all().count(), 0)

    def test_attributes(self):
        self.assertEqual(self.model.TIMEZONE, pytz.timezone('America/Los_Angeles'))

    def test_to_dict(self):
        row = self.model.objects.get(pk=1)
        self.assertDictEqual(row.to_dict(),
                             {'marginal_fuel': 9, 'total_MW': 10917.0,
                              'percent_green': 24.906, 'local_time': '2013-11-19 00:00',
                              'utc_time': '2013-11-19 08:00'})


class CAISOTestCase(BaseBATestCase, TestCase):
    """Test CAISO model"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class

    fixtures = ['caiso.json']
    model = BA_MODELS['CAISO']
    start = datetime(2013, 11, 28, tzinfo=pytz.utc)
    end = datetime(2013, 11, 29, tzinfo=pytz.utc)
    bad_start = datetime(2013, 05, 01, tzinfo=pytz.utc)
    bad_end = datetime(2013, 05, 30, tzinfo=pytz.utc)

    def test_data_available(self):
        self.assertGreater(self.model.objects.all().count(), 0)

    def test_attributes(self):
        self.assertEqual(self.model.TIMEZONE, pytz.timezone('America/Los_Angeles'))

    def test_to_dict(self):
        row = self.model.objects.get(pk=1)
        self.assertDictEqual(row.to_dict(),
                             {'percent_green': 0.002, 'marginal_fuel': 9,
                             'date_extracted': '2013-11-25 19:04', 'forecast_code': 0,
                             'total_MW': 21871.0,
                             'utc_time': '2013-11-24 09:00', 'local_time': '2013-11-24 01:00'})


class NETestCase(BaseBATestCase, TestCase):
    """Test NE model"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class

    fixtures = ['ne.json']
    model = BA_MODELS['NE']
    start = datetime(2013, 11, 29, tzinfo=pytz.utc)
    end = datetime(2013, 12, 1, tzinfo=pytz.utc)
    bad_start = datetime(2013, 05, 01, tzinfo=pytz.utc)
    bad_end = datetime(2013, 05, 30, tzinfo=pytz.utc)

    def test_data_available(self):
        self.assertGreater(self.model.objects.all().count(), 0)

    def test_attributes(self):
        self.assertEqual(self.model.TIMEZONE, pytz.timezone('America/New_York'))

    def test_to_dict(self):
        row = self.model.objects.get(pk=1)
        self.assertDictEqual(row.to_dict(),
                             {'total_MW': 13235.2, 'local_time': '2013-11-29 19:21',
                             'marginal_fuel': 2, 'percent_green': 16.137,
                             'utc_time': '2013-11-30 00:21'})
