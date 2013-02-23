from django.db import models

class CAISO(models.Model):
  pass

class BPA(models.Model):
  """Raw BPA data"""
  load = models.IntegerField()
  wind = models.IntegerField()
  thermal = models.IntegerField()
  hydro = models.IntegerField()
  thermal = models.IntegerField()
  date = models.DateTimeField()

  def get_title(self):
    return unidecode(self.wind)

class Normalized(models.Model):
  balancing_authority = models.CharField(max_length=100)
  total_watts = models.IntegerField() # capacity
  percent_clean = models.FloatField()
  curtailed = models.BooleanField(default=False)
  date = models.DateTimeField()

