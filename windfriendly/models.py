from django.db import models
from django.utils.timezone import now
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

class CAISO(models.Model):
    # load, wind, solar in MW
    load = models.FloatField()
    wind = models.FloatField()
    solar = models.FloatField()
    
    # forecast type is the index in FORECAST_CODES
    forecast_code = models.IntegerField()
    
    # date is local time at which these values will be true (can be in the future)
    date = models.DateTimeField(db_index=True)
    # date_extracted is the UTC time at which these values were pulled from CAISO
    date_extracted = models.DateTimeField(db_index=True)

    def total_load(self):
        return self.load
        
    def fraction_green(self):
        return (self.wind + self.solar) / self.load
        
    def fraction_high_carbon(self):
        return 1.0 - self.fraction_green()

    @property
    def marginal_fuel(self):
        return MARGINAL_FUELS.index('None')
        
    @classmethod
    def latest_date(cls, forecast_type):
        """Return most recent stored datetime for forecast type"""
        forecast_code = FORECAST_CODES[forecast_type]
        forecast_qset = cls.objects.filter(forecast_code=forecast_code)
        try:
            latest = forecast_qset.order_by('-date')[0]
            return latest.date
        except:
            return None
        

class BPA(models.Model):
    """Raw BPA data"""
    load = models.IntegerField()
    wind = models.IntegerField()
    thermal = models.IntegerField()
    hydro = models.IntegerField()
    date = models.DateTimeField(db_index=True)

    def get_title(self):
        return unidecode(self.wind)

    def total_load(self):
        return float(self.wind + self.hydro + self.thermal)

    def fraction_green(self):
        return self.wind / self.total_load()

    def fraction_high_carbon(self):
        return self.thermal / self.total_load()

    @property
    def marginal_fuel(self):
        return MARGINAL_FUELS.index('None')

    @classmethod
    def latest_date(cls, forecast_code=None):
        """Return most recent stored datetime for forecast type"""
        forecast_qset = cls.objects.all()
        try:
            latest = forecast_qset.order_by('-date')[0]
            return latest.date
        except:
            return None

    #def marginal_names(self):
        #return ['None']

# All units are megawatts
class NE(models.Model):
    gas = models.FloatField()
    nuclear = models.FloatField()
    hydro = models.FloatField()
    coal = models.FloatField()
    other_renewable = models.FloatField()
    other_fossil = models.FloatField()
    marginal_fuel = models.IntegerField()
    date = models.DateTimeField(db_index=True)

    def total_load(self):
        return float(self.gas + self.nuclear + self.hydro + self.coal + self.other_renewable + self.other_fossil)

    def fraction_green(self):
        return (self.hydro + self.other_renewable) / self.total_load()

    def fraction_high_carbon(self):
        return (self.coal) / self.total_load()

    @classmethod
    def latest_date(cls, forecast_code=None):
        """Return most recent stored datetime for forecast type"""
        forecast_qset = cls.objects.all()
        try:
            latest = forecast_qset.order_by('-date')[0]
            return latest.date
        except:
            return None
            
            
class Normalized(models.Model):
  balancing_authority = models.CharField(max_length=100)
  total_watts = models.IntegerField() # capacity
  percent_clean = models.FloatField()
  curtailed = models.BooleanField(default=False)
  date = models.DateTimeField(db_index=True)

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
