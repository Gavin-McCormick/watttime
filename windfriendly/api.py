from tastypie.resources import ModelResource, ALL
from tastypie import fields
from tastypie.serializers import Serializer
import json as simplejson
from django.core.serializers import json
from .balancing_authorities import BA_MODELS
from datetime import timedelta


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
        fields = ['date', 'percent_green', 'percent_dirty', 'gen_MW',
                  'marginal_fuel', 'forecast_code', 'local_date']
        serializer = MySerializer(formats=['json'])

    ####################
    # derived fields
    ####################

    # percent green
    percent_green = fields.FloatField(readonly=True,
                                      help_text="Percent of total electricity that is 'green'")
    def dehydrate_percent_green(self, bundle):
        return bundle.obj.fraction_green() * 100
        
    # percent dirty
    percent_dirty = fields.FloatField(readonly=True,
                                      help_text="Percent of total electricity that is 'dirty'")
    def dehydrate_percent_dirty(self, bundle):
        return bundle.obj.fraction_high_carbon() * 100

    # generation in megawatts
    gen_MW = fields.FloatField(readonly=True,
                               help_text="Total MW of electricty generation")
    def dehydrate_gen_MW(self, bundle):
        return bundle.obj.total_load()

    # marginal fuel code
    marginal_fuel = fields.IntegerField(readonly=True,
                                        attribute='marginal_fuel',
                                        help_text="Integer code for marginal fuel")
        
    # forecast code
    forecast_code = fields.IntegerField(readonly=True,
                                        default=0,
                                        attribute='forecast_code',
                                        help_text="Integer code for forecast type (0=actual, 1=day ahead)")
            
    # timestamp in BA's local timezone
    local_date = fields.DateTimeField(readonly=True,
                                      help_text="Timestamp in balancing authority's local time")
    def dehydrate_local_date(self, bundle):
        return bundle.obj.date.astimezone(self._meta.model.TIMEZONE)


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
        
        
# list of all resource classes
BA_RESOURCES = [BPAResource, ISONEResource, CAISOResource]