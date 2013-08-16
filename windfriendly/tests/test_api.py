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

from tastypie.test import ResourceTestCase
import pytz
from datetime import datetime, timedelta

from windfriendly.balancing_authorities import BA_MODELS
         
class BaseBAResourceTestCase(object):
    """Test generic model"""
        
    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   format='json')
        self.assertValidJSONResponse(resp)

        # check pagination
        self.assertEqual(len(self.deserialize(resp)['objects']), self.limit)
        self.assertKeys(self.deserialize(resp)['objects'][0],
                        ['date', 'local_date', 'forecast_code', 'marginal_fuel',
                         'gen_MW', 'percent_green', 'percent_dirty', 'resource_uri'])
        
    def test_get_latest(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   data={'format':'json', 'limit':1, 'order_by':'-date'})
        resp_datum = self.deserialize(resp)['objects'][0]
        model_datum = self.model.objects.all().latest()
        self.assertEqual(resp_datum['date'], model_datum.date.isoformat())
        self.assertEqual(resp_datum['percent_green'], model_datum.fraction_green*100)
        self.assertEqual(resp_datum['marginal_fuel'], model_datum.marginal_fuel)
        
       
class BPAResourceTestCase(BaseBAResourceTestCase, ResourceTestCase):
    """Test BPA API"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
    
    fixtures = ['bpa.json']
    resource_name = 'bpa'
    limit = 12*24
    model = BA_MODELS['BPA']
 
    def test_get_list_json_correct(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   format='json')
        
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'date': '2013-06-23T08:00:00+00:00', 'forecast_code': 0, 'gen_MW': 13094.0,
            'local_date': u'2013-06-23T01:00:00-07:00', 'marginal_fuel': 9,
            'percent_dirty': 5.368871238735299, 'percent_green': 0.9088131968840691,
            'resource_uri': u'/api/v1/bpa/1/'})


class CAISOResourceTestCase(BaseBAResourceTestCase, ResourceTestCase):
    """Test CAISO API"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
    
    fixtures = ['caiso.json']
    resource_name = 'caiso'
    limit = 24
    model = BA_MODELS['CAISO']
    
    def test_get_list_json_correct(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   format='json')
        
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'date': '2013-06-29T07:00:00+00:00', 'forecast_code': 0, 'gen_MW': 30374.0,
            'local_date': u'2013-06-29T00:00:00-07:00', 'marginal_fuel': 9,
            'percent_dirty': 91.70319753736749, 'percent_green': 8.296802462632513,
            'resource_uri': u'/api/v1/caiso/1/'})
            
    def test_forecast_filter(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   data={'format':'json', 'forecast_code':1})
        self.assertGreater(len(self.deserialize(resp)['objects']), 0)        

           
class NEResourceTestCase(BaseBAResourceTestCase, ResourceTestCase):
    """Test NE API"""
    # inheritance cf http://stackoverflow.com/questions/1323455/python-unit-test-with-base-and-sub-class
    
    fixtures = ['ne.json']
    resource_name = 'isone'
    limit = 12*24
    model = BA_MODELS['NE']
    
    def test_get_list_json_correct(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   format='json')
        
        # Here, we're checking an entire structure for the expected data.
        self.assertEqual(self.deserialize(resp)['objects'][0], {
            'date': u'2013-06-30T14:58:17+00:00', 'forecast_code': 0, 'gen_MW': 14644.099999999997,
            'local_date': u'2013-06-30T10:58:17-04:00', 'marginal_fuel': 2,
            'percent_dirty': 0.0, 'percent_green': 11.292602481545472,
            'resource_uri': u'/api/v1/isone/1/'})
           