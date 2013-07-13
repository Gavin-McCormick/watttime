from django.db import models
from django.utils.timezone import now
import pytz
#from accounts.models import User

# Approximately in order from bad to good
MARGINAL_FUELS = ['Coal', 'Oil', 'Natural Gas', 'Refuse', 'Hydro', 'Wood',
                  'Nuclear', 'Solar', 'Wind', 'None']
FORECAST_CODES = {'ACTUAL': 0, 'actual': 0,
                  'DAM': 1, 'dy_ahead': 1,
                  'HASP': 2, 'hr_ahead': 2,
                  'RTM': 3, 'mn_ahead': 3,
                  }

class DebugMessage(models.Model):
    date = models.DateTimeField(db_index=True)
    message = models.CharField(max_length=300)

def debug(message):
    dm = DebugMessage()
    dm.date = now()
    dm.message = message
    dm.save()
    
def group_by_hour(qset):
    """Returns a list of 24 querysets, one for each hour of the day, grouped by date.hour"""
    hour_qsets = []
    hours = ['%02d' % i for i in range(24)]
    for hour in hours:
        hour_qset = qset.filter(date__regex = ' %s:' % hour).order_by('date')
        if hour_qset.count() > 0:
            hour_qsets.append(hour_qset)
        else:
            hour_qsets.append(None)
    return hour_qsets
 
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
        return {'percent_green': round(self.fraction_green()*100, 3),
                'percent_dirty': round(self.fraction_high_carbon()*100, 3),
                'load_MW': self.total_load(),
                'marginal_fuel': self.marginal_fuel,
                'utc_time': self.date.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M'),
                'local_time': self.date.astimezone(self.TIMEZONE).strftime('%Y-%m-%d %H:%M'),
                }
                
    class Meta:
        abstract = True
    
    def get_title(self):
        return str(self.fraction_green())

    def total_load(self):
        """Total load on the grid, in MW"""
        # implement this in daughter classes
        return 0

    def fraction_green(self):
        """Fraction of load that is 'green', whatever that means"""
        # implement this in daughter classes
        return 0

    def fraction_high_carbon(self):
        """Fraction of load that is 'dirty', whatever that means"""
        # implement this in daughter classes
        return 0

    def is_unusually_green(self):
        """Boolean for whether or not this timepoint is above a 'clean' threshold"""
        return self.fraction_green() > self.GREEN_THRESHOLD

    def is_unusually_dirty(self):
        """Boolean for whether or not this timepoint is above a 'dirty' threshold"""
        return self.fraction_high_carbon() > self.DIRTY_THRESHOLD

    @classmethod
    def latest_date(cls, forecast_type=None):
        """Return most recent stored datetime for forecast type"""
        # 
        try:
            latest = cls.latest_point(forecast_type)
            return latest.date
        except:
            return None
        
    @classmethod
    def latest_point(cls, forecast_type=None):
        """Return most recent stored data point for forecast type"""
        forecast_qset = cls.objects.all()
        try:
            latest = forecast_qset.order_by('-date')[0]
            return latest
        except:
            return None
            
    @classmethod
    def earliest_date(cls, forecast_type=None):
        """Return oldest stored datetime for forecast type"""
        try:
            earliest = cls.earliest_point(forecast_type)
            return earliest.date
        except:
            return None

    @classmethod
    def earliest_point(cls, forecast_type=None):
        """Return oldest stored data point for forecast type"""
        forecast_qset = cls.objects.all()
        try:
            earliest = forecast_qset.order_by('date')[0]
            return earliest
        except:
            return None

    @classmethod
    def points_in_date_range(cls, starttime, endtime, forecast_type=None):
        """Return all data ponits in the date range for forecast type"""
        forecast_qset = cls.objects.all()
        try:
            points = forecast_qset.filter(date__range=(starttime, endtime))
            return points.order_by('date')
        except:
            return []   

    @classmethod
    def greenest_point_in_date_range(cls, starttime, endtime, forecast_type=None):
        """Return point with the highest fraction green in time period"""
        points = cls.points_in_date_range(starttime, endtime, forecast_type)
        if len(points) > 0:
            descending_points = sorted(points, reverse=True,
                                       cmp=lambda p: p.fraction_green())
            return descending_points[0]
        else:
            return None
            
    @classmethod
    def dirtiest_point_in_date_range(cls, starttime, endtime, forecast_type=None):
        """Return point with the highest fraction dirty in time period"""
        points = cls.points_in_date_range(starttime, endtime, forecast_type)
        if len(points) > 0:
            descending_points = sorted(points, reverse=True,
                                       cmp=lambda p: p.fraction_high_carbon())
            return descending_points[0]
        else:
            return None

    @classmethod
    def best_guess_points_in_date_range(cls, starttime, endtime):
        """ Return list of data points for all available timestamps in date range
                using the best available data.
        """
        # without forecasting, this is the same as point_in_date_range
        return cls.points_in_date_range(starttime, endtime)
        
    @classmethod
    def best_guess_point(cls, timestamp):
        # without forecasting, this is just the data
        try:
            return cls.objects.filter(date=timestamp)[0]
        except:
            return None
            

class BaseForecastedBalancingAuthority(BaseBalancingAuthority):
    """Abstract base class for balancing authority timepoints with forecasting"""
    class Meta:
        abstract = True
        
    # must define 'date', 'date_extracted', 'forecast_code', and 'marginal_fuel' attributes
    def to_dict(self):
        return {'percent_green': round(self.fraction_green()*100, 3),
                'percent_dirty': round(self.fraction_high_carbon()*100, 3),
                'load_MW': self.total_load(),
                'marginal_fuel': self.marginal_fuel,
                'forecast_code': self.forecast_code,
                'utc_time': self.date.astimezone(pytz.utc).strftime('%Y-%m-%d %H:%M'),
                'date_extracted': self.date_extracted.strftime('%Y-%m-%d %H:%M'),
                'local_time': self.date.astimezone(self.TIMEZONE).strftime('%Y-%m-%d %H:%M'),
                }
                
    @classmethod
    def _qset(cls, forecast_type=None):
        """ forecast_type options:
                None defaults to 'actual',
                'any' uses data from all forecast types,
                see FORECAST_CODES for others
        """
        if forecast_type == 'any':
            return cls.objects.all()
        else:
            if forecast_type is None:
                forecast_type = 'actual'
            forecast_code = FORECAST_CODES[forecast_type]
            return cls.objects.filter(forecast_code=forecast_code)

    @classmethod
    def latest_point(cls, forecast_type=None):
        """ Return most recent stored data point for forecast type.
            If multiple with same timestamp, return the most recently extracted.
        """
        try:
            qset = cls._qset(forecast_type)
            latest_date = qset.order_by('-date')[0].date
            latest_extracted = qset.filter(date=latest_date).order_by('-date_extracted')[0]
            return latest_extracted
        except:
            return None

    @classmethod
    def earliest_point(cls, forecast_type=None):
        """ Return oldest stored data point for forecast type.
            If multiple with same timestamp, return the most recently extracted.        
        """
        try:
            qset = cls._qset(forecast_type)
            earliest_date = qset.order_by('date')[0].date
            earliest_extracted = qset.filter(date=earliest_date).order_by('-date_extracted')[0]
            return earliest_extracted
        except:
            return None
                    
    @classmethod
    def points_in_date_range(cls, starttime, endtime, forecast_type=None):
        """ Return all data ponits in the date range for forecast type.
            May include multiple points with same 'date' timestamp.        
        """
        try:
            qset = cls._qset(forecast_type)
            points = qset.filter(date__range=(starttime, endtime))
            return points
        except:
            return []

    @classmethod
    def best_guess_points_in_date_range(cls, starttime, endtime):
        """ Return list of data points for all available timestamps in date range
                using the best available data.
        """
        qset = cls.objects.filter(date__range=(starttime, endtime))
        timestamps = sorted(qset.values_list('date', flat=True).distinct())
        return [cls.best_guess_point(t) for t in timestamps]

    @classmethod
    def best_guess_point(cls, timestamp):
        """ Prioritize 'actual' > 'mn_ahead' > 'hr_ahead' > 'dy_ahead' > etc.
            And prioritize most recently extracted data for each forecast type.
        """
        # get all data with timestamp
        qset = cls.objects.filter(date=timestamp)

        # if no data, return None
        if qset.count() == 0:
            return None
            
        # if there is data, get the best forecast
        preference_list = ['actual', 'mn_ahead', 'hr_ahead', 'dy_ahead']
        for forecast_type in preference_list:

            # see if there's data for this forecast
            forecast_qset = qset.filter(forecast_code=FORECAST_CODES[forecast_type])
            
            if forecast_qset.count() > 0:
                # get the most recently extracted for forecast
                return forecast_qset.order_by('-date_extracted')[0]
        

class CAISO(BaseForecastedBalancingAuthority):
    class Meta:
        abstract = False

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

    def total_load(self):
        return self.load
        
    def fraction_green(self):
        return (self.wind + self.solar) / self.load
        
    def fraction_high_carbon(self):
        return 1.0 - self.fraction_green()


class BPA(BaseBalancingAuthority):
    """Raw BPA data"""
    class Meta:
        abstract = False

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

    def total_load(self):
        return float(self.wind + self.hydro + self.thermal)

    def fraction_green(self):
        return self.wind / self.total_load()

    def fraction_high_carbon(self):
        return self.thermal / self.total_load()


# All units are megawatts
class NE(BaseBalancingAuthority):
    class Meta:
        abstract = False
        
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

    def total_load(self):
        return float(self.gas + self.nuclear + self.hydro + self.coal + self.other_renewable + self.other_fossil)

    def fraction_green(self):
        return (self.hydro + self.other_renewable) / self.total_load()

    def fraction_high_carbon(self):
        return (self.coal) / self.total_load()


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
