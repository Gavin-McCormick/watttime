from django.db import models, IntegrityError
import pytz
from windfriendly.managers import BaseBalancingAuthorityManager, ForecastedBalancingAuthorityManager
from windfriendly.settings import MARGINAL_FUELS, FORECAST_CODES
#from accounts.models import User

class BaseBalancingAuthority(models.Model):
    """Abstract base class for balancing authority timepoints"""
    # timepoints are 'extra green' if fraction_green is above this fraction
    GREEN_THRESHOLD = 0.15
    # timepoints are 'extra green' if fraction_high_carbon is above this fraction
    DIRTY_THRESHOLD = 0.95
    # must set timezone for every derived class
    TIMEZONE = pytz.utc
    
    class Meta:
        abstract = True
        get_latest_by = 'date'
        app_label = 'windfriendly'

    # must define 'date' and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_green*100, 3),
                'percent_dirty': round(self.fraction_high_carbon*100, 3),
                'load_MW': self.total_load,
                'gen_MW': self.total_gen,
                'marginal_fuel': self.marginal_fuel,
                'utc_time': self.date.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.local_date.strftime('%Y-%m-%d %H:%M'),
                }
                
    def summary_payload(self):
        return self.to_dict()

    def save_to_summary(self, summary_model):
        """Save this row to a summary table, eg Today. Returns True if old data was dropped."""
        payload = self.summary_payload()
        row = summary_model(**payload)
        try:
            row.save()
            return False
        except IntegrityError:
            # drop conflicting timestamps
            summary_model.objects.filter(utc_time=self.date, ba_name=payload['ba_name']).delete()
            # try saving again
            row.save()
            return True

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
    def total_gen(self):
        """Total generation on the grid, in MW"""
        # implement this in daughter classes
        return 0.0

    @property
    def fraction_green(self):
        """Fraction of generation that is 'green', whatever that means"""
        # implement this in daughter classes
        return 0

    @property
    def fraction_wind(self):
        """Fraction of generation that is from wind"""
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
        get_latest_by = 'date'
        app_label = 'windfriendly'

    # must define 'date', 'date_extracted', 'forecast_code', and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_green*100, 3),
                'percent_dirty': round(self.fraction_high_carbon*100, 3),
                'load_MW': self.total_load,
                'gen_MW': self.total_gen,
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
    TZ_STR = 'America/Los_Angeles'
    TIMEZONE = pytz.timezone(TZ_STR)

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
    def total_gen(self):
        """TODO: just a wrapper for load"""
        return float(self.load)

    @property
    def fraction_green(self):
        try:
            return (self.wind + self.solar) / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_wind(self):
        try:
            return self.wind / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_high_carbon(self):
        return 1.0 - self.fraction_green
        
    def summary_payload(self):
        return dict(ba_name='CAISO',
                    total_load=self.load,
                    wind=self.wind, solar=self.solar,
                    other_unknown=(self.load - self.wind - self.solar),
                    marginal_fuel=self.marginal_fuel, forecast_code=self.forecast_code,
                    percent_green=(self.fraction_green * 100),
                    percent_dirty=(self.fraction_high_carbon * 100),
                    utc_time=self.date, tz_str=self.TZ_STR
                    )


class BPA(BaseBalancingAuthority):
    """Raw BPA data"""
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone
    TZ_STR = 'America/Los_Angeles'
    TIMEZONE = pytz.timezone(TZ_STR)

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
    def total_gen(self):
        return float(self.wind + self.hydro + self.thermal)

    @property
    def total_load(self):
        return float(self.load)

    @property
    def fraction_green(self):
        try:
            return self.wind / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_wind(self):
        try:
            return self.wind / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_high_carbon(self):
        try:
            return self.thermal / self.total_gen
        except ZeroDivisionError:
            return 0

    def summary_payload(self):
        return dict(ba_name='BPA',
                    total_load=self.load, total_gen=self.total_gen,
                    wind=self.wind, hydro=self.hydro,
                    other_fossil=self.thermal,
                    marginal_fuel=self.marginal_fuel,
                    percent_green=(self.fraction_green * 100),
                    percent_dirty=(self.fraction_high_carbon * 100),
                    utc_time=self.date, tz_str=self.TZ_STR
                    )


# All units are megawatts
class NE(BaseBalancingAuthority):
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone        
    TZ_STR = 'America/New_York'
    TIMEZONE = pytz.timezone(TZ_STR)

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
    def total_gen(self):
        return float(self.gas + self.nuclear + self.hydro + self.coal + self.other_renewable + self.other_fossil)

    @property
    def total_load(self):
        """TODO: Just a wrapper around total generation for now"""
        return self.total_gen

    @property
    def fraction_green(self):
        try:
            return (self.hydro + self.other_renewable) / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_wind(self):
        try:
            return self.other_renewable / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_high_carbon(self):
        try:
            return (self.coal) / self.total_gen
        except ZeroDivisionError:
            return 0
        
    def summary_payload(self):
        return dict(ba_name='ISONE',
                    total_gen=self.total_gen,
                    other_clean=self.other_renewable, hydro=self.hydro,
                    coal=self.coal, natgas=self.gas, other_fossil=self.other_fossil,
                    nuclear=self.nuclear,
                    marginal_fuel=self.marginal_fuel,
                    percent_green=(self.fraction_green * 100),
                    percent_dirty=(self.fraction_high_carbon * 100),
                    utc_time=self.date, tz_str=self.TZ_STR
                    )


class MISO(BaseForecastedBalancingAuthority):
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone        
    TZ_STR = 'America/Chicago'
    TIMEZONE = pytz.timezone(TZ_STR)

    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField(default=FORECAST_CODES['actual'])

    # generation and load in MW
    gas = models.FloatField()
    nuclear = models.FloatField()
    other_gen = models.FloatField() # Hydro, Pumped Storage Hydro, Diesel, Demand Response Resources, External Asynchronous Resources and a varied assortment of solid waste, garbage and wood pulp burners
    coal = models.FloatField()
    wind = models.FloatField()
    load = models.FloatField()

    # date is utc
    date = models.DateTimeField(db_index=True)
    # date_extracted is the UTC time at which these values were pulled from MISO
    date_extracted = models.DateTimeField(db_index=True)

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')

    @property
    def total_load(self):
        return self.load
        
    @property
    def total_gen(self):
        return self.gas + self.coal + self.nuclear + self.wind + self.other_gen

    @property
    def fraction_green(self):
        try:
            return (self.wind) / self.total_gen
        except ZeroDivisionError:
            return 0
        
    @property
    def fraction_wind(self):
        try:
            return (self.wind) / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_high_carbon(self):
        try:
            return (self.coal) / self.total_gen       
        except ZeroDivisionError:
            return 0

    def summary_payload(self):
        return dict(ba_name='MISO',
                    total_gen=self.total_gen, total_load=self.load,
                    wind=self.wind, other_unknown=self.other_gen,
                    coal=self.coal, natgas=self.gas, nuclear=self.nuclear,
                    marginal_fuel=self.marginal_fuel, forecast_code=self.forecast_code,
                    percent_green=(self.fraction_green * 100),
                    percent_dirty=(self.fraction_high_carbon * 100),
                    utc_time=self.date, tz_str=self.TZ_STR
                    )


class PJM(BaseForecastedBalancingAuthority):
    """Raw PJM data"""
    # use non-forecasted manager
    objects = BaseBalancingAuthorityManager()

    # timezone
    TZ_STR = 'America/New_York'
    TIMEZONE = pytz.timezone(TZ_STR)

    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField(default=FORECAST_CODES['actual'])

    # load, etc in MW
    load = models.IntegerField()
    wind = models.IntegerField()

    # date is utc
    date = models.DateTimeField(db_index=True)
    # date_extracted is the UTC time at which these values were pulled from MISO
    date_extracted = models.DateTimeField(db_index=True)

    @property
    def marginal_fuel(self):
        """Integer code for marginal fuel"""
        # implement this as an actual field for BAs with data
        return MARGINAL_FUELS.index('None')

    @property
    def total_gen(self):
        return float(self.load)

    @property
    def total_load(self):
        return float(self.load)

    @property
    def fraction_green(self):
        try:
            return self.wind / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_wind(self):
        try:
            return self.wind / self.total_gen
        except ZeroDivisionError:
            return 0

    @property
    def fraction_high_carbon(self):
        return 1 - self.fraction_wind

    def summary_payload(self):
        return dict(ba_name='PJM',
                    total_load=self.load,
                    wind=self.wind, other_unknown=(self.load - self.wind),
                    marginal_fuel=self.marginal_fuel, forecast_code=self.forecast_code,
                    percent_green=(self.fraction_green * 100),
                    percent_dirty=(self.fraction_high_carbon * 100),
                    utc_time=self.date, tz_str=self.TZ_STR
                    )
