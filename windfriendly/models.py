from django.db import models

class CAISO(models.Model):
  pass

class BPA(models.Model):
  """Raw BPA data"""
  load = models.IntegerField()
  wind = models.IntegerField()
  thermal = models.IntegerField()
  hydro = models.IntegerField()
 # thermal = models.IntegerField()
  date = models.DateTimeField(db_index=True)

  def get_title(self):
    return unidecode(self.wind)

# All units are megawatts
class NE(models.Model):
    gas = models.FloatField()
    nuclear = models.FloatField()
    hydro = models.FloatField()
    coal = models.FloatField()
    other_renewable = models.FloatField()
    other_fossil = models.FloatField()
    date = models.DateTimeField()

class Normalized(models.Model):
  balancing_authority = models.CharField(max_length=100)
  total_watts = models.IntegerField() # capacity
  percent_clean = models.FloatField()
  curtailed = models.BooleanField(default=False)
  date = models.DateTimeField()

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
