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
    maxDiff = None
        
    def test_get_list_json(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   format='json')
        self.assertValidJSONResponse(resp)

        # check pagination
        self.assertLessEqual(len(self.deserialize(resp)['objects']), self.limit)
        self.assertKeys(self.deserialize(resp)['objects'][0],
                        ['date', 'local_date', 'date_extracted', 'forecast_code', 'marginal_fuel',
                         'total_MW', 'fraction_clean', 'resource_uri'])
        
    def test_get_latest(self):
        resp = self.api_client.get('/api/v1/%s/' % self.resource_name,
                                   data={'format':'json', 'limit':1, 'order_by':'-date'})
        resp_datum = self.deserialize(resp)['objects'][0]
        model_datum = self.model.objects.all().latest()
        self.assertEqual(resp_datum['date'], model_datum.date.isoformat())
        self.assertEqual(resp_datum['fraction_clean'], model_datum.fraction_clean)
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
            'date': '2013-11-19T08:00:00+00:00', 'date_extracted': '2013-11-19T08:00:00+00:00', 
            'forecast_code': 0, 'total_MW': 10917.0,
            'local_date': u'2013-11-19T00:00:00-08:00', 'marginal_fuel': 9,
            'fraction_clean': 0.24906109737107263,
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
            'date': '2013-11-24T09:00:00+00:00', 'date_extracted': '2013-11-25T19:04:45+00:00',
            'forecast_code': 0, 'total_MW': 21871.0,
            'local_date': u'2013-11-24T01:00:00-08:00', 'marginal_fuel': 9,
            'fraction_clean': 1.6873942663801407e-05,
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
            'date': u'2013-11-30T00:21:38+00:00', 'date_extracted': u'2013-11-30T00:27:29+00:00', 
            'forecast_code': 0, 'total_MW': 13235.2,
            'local_date': u'2013-11-29T19:21:38-05:00', 'marginal_fuel': 2,
            'fraction_clean': 0.16137270309477758,
            'resource_uri': u'/api/v1/isone/1/'})
           