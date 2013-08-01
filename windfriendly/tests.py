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

from .balancing_authorities import BALANCING_AUTHORITIES, BA_MODELS, BA_PARSERS

class BAInfoTestCase(TestCase):
    """Test contents of balancing_authorities.py"""
    
    def test_supported_states(self):
        for st in ['CA', 'CT', 'ID', 'MA', 'ME', 'NH', 'OR', 'RI', 'VT', 'WA']:
            self.assertIn(st, BALANCING_AUTHORITIES.keys())
            
    def test_supported_bas(self):
        for ba in ['BPA', 'ISONE', 'CAISO']:
            self.assertIn(ba, BA_MODELS.keys())
            self.assertIn(ba, BA_PARSERS.keys())
            
         
class BaseBATestCase(object):
    """Test BPA model"""
        
    def test_fractions(self):
        row = self.model.objects.get(pk=1)
        self.assertLess(row.fraction_green(), 1)
        self.assertGreater(row.fraction_green(), 0)
        self.assertLess(row.fraction_high_carbon(), 1)
        self.assertGreater(row.fraction_high_carbon, 0)
                                        
    def test_latest(self):
        self.assertEqual(self.model.objects.latest_date(), self.model.objects.latest_point().date)
        self.assertEqual(self.model.objects.earliest_date(), self.model.objects.earliest_point().date)
        
    def test_points_in_date_range(self):
        rows = self.model.objects.points_in_date_range(self.start, self.end)
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
        rows = self.model.objects.points_in_date_range(self.bad_start, self.bad_end)
        
        # should be empty queryset
        self.assertEqual(rows.count(), 0)
        
    def test_points_in_date_range_bad_dates(self):
        rows = self.model.objects.points_in_date_range(self.end, self.start)
        
        # should be empty queryset
        self.assertEqual(rows.count(), 0)
        
    def test_best_guess(self):
        r_by_pk = self.model.objects.get(pk=1)
        r_by_date = self.model.objects.best_guess_point(r_by_pk.date)
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
    start = datetime(2013, 06, 25, tzinfo=pytz.utc)
    end = datetime(2013, 06, 26, tzinfo=pytz.utc)
    bad_start = datetime(2013, 05, 01, tzinfo=pytz.utc)
    bad_end = datetime(2013, 05, 30, tzinfo=pytz.utc)
    
    def test_data_available(self):
        self.assertGreater(self.model.objects.all().count(), 0)
        
    def test_attributes(self):
        self.assertEqual(self.model.TIMEZONE, pytz.timezone('US/Pacific'))
        self.assertEqual(self.model.GREEN_THRESHOLD, 0.15)
        self.assertEqual(self.model.DIRTY_THRESHOLD, 0.95)
        
    def test_to_dict(self):
        row = self.model.objects.get(pk=1)
        self.assertDictEqual(row.to_dict(),
                             {'marginal_fuel': 9, 'percent_dirty': 5.369, 'load_MW': 13094.0,
                              'percent_green': 0.909, 'local_time': '2013-06-23 01:00', 
                              'utc_time': '2013-06-23 08:00'})

           
class NETestCase(BaseBATestCase, TestCase):
    """Test BPA model"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
    
    fixtures = ['ne.json']
    model = BA_MODELS['NE']
    start = datetime(2013, 07, 13, tzinfo=pytz.utc)
    end = datetime(2013, 07, 14, tzinfo=pytz.utc)
    bad_start = datetime(2013, 05, 01, tzinfo=pytz.utc)
    bad_end = datetime(2013, 05, 30, tzinfo=pytz.utc)
    
    def test_data_available(self):
        self.assertGreater(self.model.objects.all().count(), 0)
        
    def test_attributes(self):
        self.assertEqual(self.model.TIMEZONE, pytz.timezone('US/Eastern'))
        self.assertEqual(self.model.GREEN_THRESHOLD, 0.15)
        self.assertEqual(self.model.DIRTY_THRESHOLD, 0.95)
        
    def test_to_dict(self):
        row = self.model.objects.get(pk=1)
        self.assertDictEqual(row.to_dict(),
                             {'load_MW': 14644.099999999997, 'local_time': '2013-06-30 10:58',
                             'marginal_fuel': 2, 'percent_dirty': 0.0, 'percent_green': 11.293,
                             'utc_time': '2013-06-30 14:58'})

           