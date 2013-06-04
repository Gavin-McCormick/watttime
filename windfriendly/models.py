from django.db import models
#from accounts.models import User

class CAISO(models.Model):
  pass

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
    return None

# All units are megawatts
class NE(models.Model):
    gas = models.FloatField()
    nuclear = models.FloatField()
    hydro = models.FloatField()
    coal = models.FloatField()
    other_renewable = models.FloatField()
    other_fossil = models.FloatField()
    marginal_fuel = models.IntegerField() # See parsers.py for meaning
    date = models.DateTimeField(db_index=True)

    def total_load(self):
      return float(self.gas + self.nuclear + self.hydro + self.coal + self.other_renewable + self.other_fossil)
    
    def fraction_green(self):
      return (self.hydro + self.other_renewable) / self.total_load()
    
    def fraction_high_carbon(self):
      return (self.coal) / self.total_load()
    
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
    return row.cost * row.duration / 3600.0 / 10000.0
