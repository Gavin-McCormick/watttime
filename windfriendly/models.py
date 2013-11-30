from django.db import models
import pytz
from .managers import BaseBalancingAuthorityManager, ForecastedBalancingAuthorityManager
from .settings import MARGINAL_FUELS, FORECAST_CODES
from datetime import datetime
#from accounts.models import User

class BaseBalancingAuthority(models.Model):
    """Abstract base class for balancing authority timepoints"""
    # must set timezone for every derived class
    TIMEZONE = pytz.utc

    #### COMMON FIELDS ####
    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField(default=0)
    # date is utc
    date = models.DateTimeField(db_index=True)
    # date_extracted is the UTC time at which these values were pulled from ISO
    date_extracted = models.DateTimeField(db_index=True)
    # fraction_clean is fraction of generation from clean sources (eg wind)
    fraction_clean = models.FloatField(default=0)
    # total_MW is the total amount of generation, if available, or load, if not
    total_MW = models.FloatField(default=0)

    # must define 'date' and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_clean*100, 3),
                'total_MW': self.total_MW,
                'marginal_fuel': self.marginal_fuel,
                'utc_time': self.date.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.local_date.strftime('%Y-%m-%d %H:%M'),
                }

    class Meta:
        abstract = True
        get_latest_by = 'date'

    def get_title(self):
        return str(self.fraction_clean)

    @property
    def local_date(self):
        """ Time in local timezone """
        return self.date.astimezone(self.TIMEZONE)


class BaseForecastedBalancingAuthority(BaseBalancingAuthority):
    """Abstract base class for balancing authority timepoints with forecasting"""
    class Meta:
        abstract = True
        get_latest_by = 'date'

    # must define 'date', 'date_extracted', 'forecast_code', and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_clean*100, 3),
                'total_MW': self.total_MW,
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
    TIMEZONE = pytz.timezone('America/Los_Angeles')

    # load, wind, solar in MW
    load = models.FloatField()
    wind = models.FloatField()
    solar = models.FloatField()

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')


class BPA(BaseBalancingAuthority):
    """Raw BPA data"""
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone
    TIMEZONE = pytz.timezone('America/Los_Angeles')

    # load, etc in MW
    load = models.IntegerField()
    wind = models.IntegerField()
    thermal = models.IntegerField()
    hydro = models.IntegerField()

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')


# All units are megawatts
class NE(BaseBalancingAuthority):
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone        
    TIMEZONE = pytz.timezone('America/New_York')

    # load, etc in MW
    gas = models.FloatField()
    nuclear = models.FloatField()
    hydro = models.FloatField()
    coal = models.FloatField()
    other_renewable = models.FloatField()
    other_fossil = models.FloatField()
    marginal_fuel = models.IntegerField()


class MISO(BaseForecastedBalancingAuthority):
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone        
    TIMEZONE = pytz.timezone('America/Chicago')

    # generation and load in MW
    gas = models.FloatField()
    nuclear = models.FloatField()
    other_gen = models.FloatField() # Hydro, Pumped Storage Hydro, Diesel, Demand Response Resources, External Asynchronous Resources and a varied assortment of solid waste, garbage and wood pulp burners
    coal = models.FloatField()
    wind = models.FloatField()
    load = models.FloatField()

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')


class PJM(BaseForecastedBalancingAuthority):
    """Raw PJM data"""
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone
    TIMEZONE = pytz.timezone('US/Eastern')

    # load, etc in MW
    load = models.IntegerField()
    wind = models.IntegerField()

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')


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

