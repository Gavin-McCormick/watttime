from django.db import models
from django.db.models.query import QuerySet
from django.core.exceptions import FieldError
from datetime import datetime
import pytz
import numpy as np
from .settings import FORECAST_CODES

class TimeseriesQuerySet(QuerySet):
    def max_by_attribute(self, attr):
        """Return point with the highest value of the named attribute in queryset"""
        if self.count() > 0:
            try: # if db field
                return self.order_by('-'+attr)[0]
            except : # if property
                return max(self, key=lambda p: getattr(p, attr))
        else: # if no data
            return None

    def min_by_attribute(self, attr):
        """Return point with the lowest value of the named attribute in queryset"""
        if self.count() > 0:
            try: # if db field
                return self.order_by(attr)[0]
            except : # if property
                return min(self, key=lambda p: getattr(p, attr))
        else: # if no data
            return None
            
    def earliest(self):
        """ Return oldest stored data point in queryset.
            If multiple with same timestamp, return the most recently extracted.        
        """
        try:
            r = self.order_by('date')[0]
        except IndexError: # if no data
            return None
        if 'date_extracted' in dir(r): # filter on secondary time dimension
            return self.filter(date=r.date).order_by('-date_extracted')[0]
        else: # if no secondary time dimension
            return r

    def latest(self):
        """ Return newest stored data point in queryset.
            If multiple with same timestamp, return the most recently extracted.        
        """
        try:
            r = self.order_by('-date')[0]
        except IndexError: # if no data
            return None
        if 'date_extracted' in dir(r): # filter on secondary time dimension
            return self.filter(date=r.date).order_by('-date_extracted')[0]
        else: # if no secondary time dimension
            return r

    def best_guess(self):
        """ Without forecast, this is alias for latest """
        return self.latest()
        
    def best_guess_points(self):
        """ Return list of data points for all available timestamps in date range
                using the best available data.
        """
        timestamps = sorted(self.values_list('date', flat=True).distinct())
        return [self.filter(date=t).best_guess() for t in timestamps]


class ForecastedTimeseriesQuerySet(TimeseriesQuerySet):
    def best_guess(self):
        """ Prioritize 'actual' > 'mn_ahead' > 'hr_ahead' > 'dy_ahead' > etc.
            And prioritize most recently extracted data for each forecast type.
        """
        # if no data, return None
        if self.count() == 0:
            return None
                    
        # if there is data, get the best forecast
        preference_list = ['actual', 'mn_ahead', 'hr_ahead', 'dy_ahead']
        for forecast_type in preference_list:

            # see if there's data for this forecast
            forecast_qset = self.filter(forecast_code=FORECAST_CODES[forecast_type])
            if forecast_qset.count() > 0:
                return forecast_qset.latest()


class BaseBalancingAuthorityManager(models.Manager):
    """Model Manager for Balancing Authority models without forecasting"""
    def get_queryset(self):
        return TimeseriesQuerySet(self.model, using=self._db)
                    
    def greenest_subrange(self, starttime, endtime, timedelta, forecast_type=None):
        """ Return a queryset covering time period of length timedelta that is the
            greenest between starttime and endtime (inclusive).
        """
        # get full range
        if forecast_type is None:
            rows = self.get_queryset().filter(date__range=(starttime, endtime)).best_guess_points()
        else:
            rows = self.get_queryset().filter(date__range=(starttime, endtime),
                                               forecast_code=FORECAST_CODES[forecast_type])
               
        # find best subrange
        green_points = {r.date: r.fraction_clean for r in rows}
        times = sorted(green_points.keys())
        greens = [green_points[d] for d in times]
        time_pairs = [(d, d + timedelta) for d in times
                                         if d + timedelta <= times[-1]]
        
        # get best data
        best_green = 0
        best_timepair = None
        best_rows = None
        for slice_start, time_pair in enumerate(time_pairs):
            try:
                # get exact match
                slice_end = times.index(time_pair[1])
            except ValueError:
                # get close match
                for slice_end in range(slice_start, len(time_pairs)):
                    if times[slice_end] > time_pair[1]:
                        break
                
            avg_green = np.mean(greens[slice_start:slice_end])
            if avg_green > best_green:
                best_green = avg_green
                best_timepair = time_pair
                best_rows = rows[slice_start:slice_end]
                    
        # return
        return best_rows, best_timepair, best_green, np.mean(greens)
        
    def average_day(self, utc_start, utc_end, tz):
        # get rows
        try:
            ba_rows = self.get_queryset().filter(date__range=(utc_start, utc_end), forecast_code=0)
        except FieldError:
            ba_rows = self.get_queryset().filter(date__range=(utc_start, utc_end))
            
        if ba_rows.count() == 0:
            print 'no data for UTC start %s, end %s' % (repr(utc_start), repr(utc_end))
            return []

        # collect data
        data = []
        for hour in range(24):
            group = ba_rows.filter(date__hour=hour)
            if group.count() > 0:
                # get average data
                total_green = 0
                total_MW = 0
                count = 0.0
                for r in group:
                    if r.total_MW > 0: # don't try to handle bad data
                        total_green += r.fraction_clean
                        total_MW += r.total_MW
                        count += 1.0
                average_green = round(total_green*100/count, 3)
                average_gen = total_MW/count
                representative_date = group.latest().local_date.replace(minute=0)
            else:
                # get null data
                average_green = None
                average_gen = None
                representative_date = ba_rows.latest().local_date.replace(hour=hour, minute=0)
    
            # complicated date wrangling to get all local_time values in local today
            latest_dt = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz)
            local_time = representative_date.replace(year=latest_dt.year,
                                                     month=latest_dt.month,
                                                     day=latest_dt.day)
            utc_time = local_time.astimezone(pytz.utc)
    
            # add to list
            data.append({"percent_green": average_green,
                         "gen_MW": average_gen,
                         "utc_time": utc_time.strftime('%Y-%m-%d %H:%M'),
                         "local_time": local_time.strftime('%Y-%m-%d %H:%M'),
                         "hour": local_time.hour,
                        })

        # return
        return sorted(data, key=lambda r: r['local_time'])


class ForecastedBalancingAuthorityManager(BaseBalancingAuthorityManager):
    def get_queryset(self, forecast_type='any'):
        """ forecast_type options:
                None defaults to 'actual',
                'any' uses data from all forecast types,
                see FORECAST_CODES for others
        """
        qset = ForecastedTimeseriesQuerySet(self.model, using=self._db)
        if forecast_type == 'any':
            return qset
        else:
            if forecast_type is None:
                forecast_type = 'actual'
            forecast_code = FORECAST_CODES[forecast_type]
            return qset.filter(forecast_code=forecast_code)

