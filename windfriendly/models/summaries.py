from django.db import models
import pytz

class BaseSummary(models.Model):
    """Abstract base class for summary statistics"""

    class Meta:
        abstract = True
        app_label = 'windfriendly'
        unique_together = ('utc_time', 'ba_name')

    # name of balancing authority
    ba_name = models.CharField(max_length=100)

    # all of these are in MW
    # totals
    total_load = models.FloatField(null=True, blank=True)
    total_gen = models.FloatField(null=True, blank=True)
    # renewables and other clean
    wind = models.FloatField(null=True, blank=True)
    solar = models.FloatField(null=True, blank=True)
    hydro = models.FloatField(null=True, blank=True)
    other_clean = models.FloatField(null=True, blank=True)
    # fossil and other dirty
    coal = models.FloatField(null=True, blank=True)
    natgas = models.FloatField(null=True, blank=True)
    other_fossil = models.FloatField(null=True, blank=True)
    # other
    nuclear = models.FloatField(null=True, blank=True)
    other_unknown = models.FloatField(null=True, blank=True)
    
    # percent clean and dirty
    percent_green = models.FloatField()
    percent_dirty = models.FloatField()

    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField(default=0)
    # marginal_fuel is the index in MARGINAL_FUELS
    marginal_fuel = models.IntegerField(null=True, blank=True)

    # time is UTC time at which these values will be true (can be in the future)
    utc_time = models.DateTimeField()
    tz_str = models.CharField(max_length=100)   

    def fuel_mix(self):
        return {
                 'wind': self.wind, 'solar': self.solar, 'hydro': self.hydro,
                 'coal': self.coal, 'natgas': self.natgas, 'nuclear': self.nuclear,
                 'other_fossil': self.other_fossil, 'other_clean': self.other_clean,
                 'other_unknown': self.other_unknown,
                 }

    def to_dict(self):
        return {'percent_green': round(self.percent_green, 3),
                'percent_dirty': round(self.percent_dirty, 3),
                'load_MW': self.total_load,
                'gen_MW': self.total_gen,
                'marginal_fuel': self.marginal_fuel,
                'forecast_code': self.forecast_code,
                'utc_time': self.utc_time.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.utc_time.astimezone(pytz.timezone(self.tz_str)).strftime('%Y-%m-%d %H:%M'),
                'fuel_mix': self.fuel_mix(),
                'ba_name': self.ba_name,
                }


class Today(BaseSummary):
    pass
