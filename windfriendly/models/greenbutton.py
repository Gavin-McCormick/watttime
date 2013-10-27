from django.db import models

class User(models.Model):
    # name
    name = models.CharField(max_length=100)

    class Meta:
        app_label = 'windfriendly'


class MeterReading(models.Model):
    class Meta:
        app_label = 'windfriendly'
        
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
