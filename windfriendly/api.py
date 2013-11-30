from tastypie.resources import ModelResource, ALL #, trailing_slash
from tastypie import fields
from tastypie.serializers import Serializer
#from django.conf.urls import url
import json as simplejson
from django.core.serializers import json
from .balancing_authorities import BA_MODELS
from datetime import timedelta #, datetime
#import pytz


class MySerializer(Serializer):
    def format_datetime(self, data):
        """ Override default time behavior to keep timezone awareness """
     #   data = make_naive(data)
        if self.datetime_formatting == 'rfc-2822':
            return format_datetime(data)
        if self.datetime_formatting == 'iso-8601-strict':
            # Remove microseconds to strictly adhere to iso-8601
            data = data - timedelta(microseconds = data.microsecond)
            
        return data.isoformat()
        
    json_indent = 2
    def to_json(self, data, options=None):
        """ Pretty-print JSON """
        options = options or {}
        data = self.to_simple(data, options)
        return simplejson.dumps(data, cls=json.DjangoJSONEncoder,
                sort_keys=True, ensure_ascii=False, indent=self.json_indent)
    

class BalancingAuthorityResource(ModelResource):    
    class Meta:
        queryset = BA_MODELS['BPA'].objects.all() # dummy, but needed for for concreteness
        allowed_methods = ['get']
        ordering = ['date']
        filtering = {
            'date': ALL,
            'forecast_code': ['exact'],
            'marginal_fuel': ['exact'],
        }
        fields = ['date', 'fraction_clean', 'total_MW',
                  'marginal_fuel', 'forecast_code', 'local_date', 'date_extracted']
        serializer = MySerializer(formats=['json'])

    ####################
    # derived fields
    ####################

    # marginal fuel code
    marginal_fuel = fields.IntegerField(readonly=True,
                                        attribute='marginal_fuel',
                                        help_text="Integer code for marginal fuel")
    def dehydrate_marginal_fuel(self, bundle):
        return bundle.obj.marginal_fuel
        
    # timestamp in BA's local timezone
    local_date = fields.DateTimeField(readonly=True,
                                      help_text="Timestamp in balancing authority's local time")
    def dehydrate_local_date(self, bundle):
        return bundle.obj.local_date


class BPAResource(BalancingAuthorityResource):
    """ Resource for BPA model """
    class Meta(BalancingAuthorityResource.Meta):
        resource_name = 'bpa'
        model = BA_MODELS[resource_name.upper()]
        queryset = model.objects.all()
        limit = 12*24 # 24 hours of 5-minute data
        

class ISONEResource(BalancingAuthorityResource):
    """ Resource for NE model """
    class Meta(BalancingAuthorityResource.Meta):
        resource_name = 'isone'
        model = BA_MODELS[resource_name.upper()]
        queryset = model.objects.all()
        limit = 12*24 # 24 hours of 5-minute data

        
class CAISOResource(BalancingAuthorityResource):
    """ Resource for CAISO model """
    class Meta(BalancingAuthorityResource.Meta):
        resource_name = 'caiso'
        model = BA_MODELS[resource_name.upper()]
        queryset = model.objects.all()
        limit = 24 # 24 hours of hourly data
        

class MISOResource(BalancingAuthorityResource):
    """ Resource for MISO model """
    class Meta(BalancingAuthorityResource.Meta):
        resource_name = 'miso'
        model = BA_MODELS[resource_name.upper()]
        queryset = model.objects.all()
        limit = 12*24 # 24 hours of 5-minute data
        
class PJMResource(BalancingAuthorityResource):
    """ Resource for MISO model """
    class Meta(BalancingAuthorityResource.Meta):
        resource_name = 'pjm'
        model = BA_MODELS[resource_name.upper()]
        queryset = model.objects.all()
        limit = 6*24 # 24 hours of 5-minute data
      
# list of all resource classes
BA_RESOURCES = [BPAResource, ISONEResource, CAISOResource, MISOResource, PJMResource]
