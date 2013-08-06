from django.db import models
import pytz
from .managers import BaseBalancingAuthorityManager, ForecastedBalancingAuthorityManager
from .settings import MARGINAL_FUELS
#from accounts.models import User

class BaseBalancingAuthority(models.Model):
    """Abstract base class for balancing authority timepoints"""
    # timepoints are 'extra green' if fraction_green is above this fraction
    GREEN_THRESHOLD = 0.15
    # timepoints are 'extra green' if fraction_high_carbon is above this fraction
    DIRTY_THRESHOLD = 0.95
    # must set timezone for every derived class
    TIMEZONE = pytz.utc

    # must define 'date' and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_green*100, 3),
                'percent_dirty': round(self.fraction_high_carbon*100, 3),
                'load_MW': self.total_load,
                'marginal_fuel': self.marginal_fuel,
                'utc_time': self.date.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.local_date.strftime('%Y-%m-%d %H:%M'),
                }

    class Meta:
        abstract = True

    def get_title(self):
        return str(self.fraction_green)

    @property
    def local_date(self):
        """ Time in local timezone """
        return self.date.astimezone(self.TIMEZONE)

    @property
    def total_load(self):
        """Total load on the grid, in MW"""
        # implement this in daughter classes
        return 0.0

    @property
    def fraction_green(self):
        """Fraction of load that is 'green', whatever that means"""
        # implement this in daughter classes
        return 0

    @property
    def fraction_high_carbon(self):
        """Fraction of load that is 'dirty', whatever that means"""
        # implement this in daughter classes
        return 0

    def is_unusually_green(self):
        """Boolean for whether or not this timepoint is above a 'clean' threshold"""
        return self.fraction_green > self.GREEN_THRESHOLD

    def is_unusually_dirty(self):
        """Boolean for whether or not this timepoint is above a 'dirty' threshold"""
        return self.fraction_high_carbon > self.DIRTY_THRESHOLD


class BaseForecastedBalancingAuthority(BaseBalancingAuthority):
    """Abstract base class for balancing authority timepoints with forecasting"""
    class Meta:
        abstract = True
        
    # must define 'date', 'date_extracted', 'forecast_code', and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_green*100, 3),
                'percent_dirty': round(self.fraction_high_carbon*100, 3),
                'load_MW': self.total_load,
                'marginal_fuel': self.marginal_fuel,
                'forecast_code': self.forecast_code,
                'utc_time': self.date.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M'),
                'date_extracted': self.date_extracted.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.local_date.strftime('%Y-%m-%d %H:%M'),
                }
        

class CAISO(BaseForecastedBalancingAuthority):
    # use forecasting manager
    objects = ForecastedBalancingAuthorityManager()    
    
    # timezone
    TIMEZONE = pytz.timezone('US/Pacific')
        
    # load, wind, solar in MW
    load = models.FloatField()
    wind = models.FloatField()
    solar = models.FloatField()
    
    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField()
    
    # date is UTC time at which these values will be true (can be in the future)
    date = models.DateTimeField(db_index=True)
    # date_extracted is the UTC time at which these values were pulled from CAISO
    date_extracted = models.DateTimeField(db_index=True)

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')

    @property
    def total_load(self):
        return float(self.load)
        
    @property
    def fraction_green(self):
        return (self.wind + self.solar) / self.load
        
    @property
    def fraction_high_carbon(self):
        return 1.0 - self.fraction_green


class BPA(BaseBalancingAuthority):
    """Raw BPA data"""
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone
    TIMEZONE = pytz.timezone('US/Pacific')
        
    # load, etc in MW
    load = models.IntegerField()
    wind = models.IntegerField()
    thermal = models.IntegerField()
    hydro = models.IntegerField()
    
    # date is utc
    date = models.DateTimeField(db_index=True)

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')

    @property
    def total_load(self):
        return float(self.wind + self.hydro + self.thermal)

    @property
    def fraction_green(self):
        return self.wind / self.total_load

    @property
    def fraction_high_carbon(self):
        return self.thermal / self.total_load


# All units are megawatts
class NE(BaseBalancingAuthority):
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone        
    TIMEZONE = pytz.timezone('US/Eastern')
        
    # load, etc in MW
    gas = models.FloatField()
    nuclear = models.FloatField()
    hydro = models.FloatField()
    coal = models.FloatField()
    other_renewable = models.FloatField()
    other_fossil = models.FloatField()
    marginal_fuel = models.IntegerField()

    # date is utc
    date = models.DateTimeField(db_index=True)

    @property
    def total_load(self):
        return float(self.gas + self.nuclear + self.hydro + self.coal + self.other_renewable + self.other_fossil)

    @property
    def fraction_green(self):
        return (self.hydro + self.other_renewable) / self.total_load

    @property
    def fraction_high_carbon(self):
        return (self.coal) / self.total_load


class User(models.Model):
    # name
    name = models.CharField(max_length=100)


class MeterReading(models.Model):
  # user id
  userid = models.ForeignKey(User)

  # energy in kwh
  energy = models.FloatField()
  
  # duration in seconds
  duration = models.IntegerField()
  
  # start time in date-time
  start = models.DateTimeField(db_index=True)

  # cost in dollars
  cost = models.FloatField()

  def total_kwh(self):
    return self.energy/3600.0 * self.duration
  
  def total_cost(self):
    return self.cost * self.duration / 3600.0 / 10000.0
