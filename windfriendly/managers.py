from django.db import models
import numpy as np
from .settings import FORECAST_CODES


class BaseBalancingAuthorityManager(models.Manager):
    """Model Manager for Balancing Authority models without forecasing"""

    def latest_date(self, forecast_type=None):
        """Return most recent stored datetime for forecast type"""
        # 
        try:
            latest = self.latest_point(forecast_type)
            return latest.date
        except:
            return None
        
    def latest_point(self, forecast_type=None):
        """Return most recent stored data point for forecast type"""
        forecast_qset = self.get_query_set()
        try:
            latest = forecast_qset.order_by('-date')[0]
            return latest
        except:
            return None
            
    def earliest_date(self, forecast_type=None):
        """Return oldest stored datetime for forecast type"""
        try:
            earliest = self.earliest_point(forecast_type)
            return earliest.date
        except:
            return None

    def earliest_point(self, forecast_type=None):
        """Return oldest stored data point for forecast type"""
        forecast_qset = self.get_query_set()
        try:
            earliest = forecast_qset.order_by('date')[0]
            return earliest
        except:
            return None

    def points_in_date_range(self, starttime, endtime, forecast_type=None):
        """Return all data ponits in the date range for forecast type, ordered by date"""
        forecast_qset = self.get_query_set()
        try:
            points = forecast_qset.filter(date__range=(starttime, endtime))
            return points.order_by('date')
        except:
            return self.get_query_set().none()

    def greenest_point_in_date_range(self, starttime, endtime, forecast_type=None):
        """Return point with the highest fraction green in time period"""
        points = self.points_in_date_range(starttime, endtime, forecast_type)
        if len(points) > 0:
            descending_points = sorted(points, reverse=True,
                                       cmp=lambda p: p.fraction_green())
            return descending_points[0]
        else:
            return None
            
    def dirtiest_point_in_date_range(self, starttime, endtime, forecast_type=None):
        """Return point with the highest fraction dirty in time period"""
        points = self.points_in_date_range(starttime, endtime, forecast_type)
        if len(points) > 0:
            descending_points = sorted(points, reverse=True,
                                       cmp=lambda p: p.fraction_high_carbon())
            return descending_points[0]
        else:
            return None

    def best_guess_points_in_date_range(self, starttime, endtime):
        """ Return list of data points for all available timestamps in date range
                using the best available data.
        """
        # without forecasting, this is the same as point_in_date_range
        return self.points_in_date_range(starttime, endtime)
        
    def best_guess_point(self, timestamp):
        # without forecasting, this is just the data
        try:
            return self.get_query_set().filter(date=timestamp)[0]
        except:
            return None
            
    def greenest_subrange(self, starttime, endtime, timedelta, forecast_type=None):
        """ Return a queryset covering time period of length timedelta that is the
            greenest between starttime and endtime (inclusive).
        """
        # get full range
        if forecast_type is None:
            rows = self.best_guess_points_in_date_range(starttime, endtime)
        else:
            rows = self.points_in_date_range(starttime, endtime, forecast_type)
               
        # find best subrange
        green_points = {r.date: r.fraction_green() for r in rows}
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
        
        
class ForecastedBalancingAuthorityManager(BaseBalancingAuthorityManager):
    def get_query_set(self, forecast_type=None):
        """ forecast_type options:
                None defaults to 'actual',
                'any' uses data from all forecast types,
                see FORECAST_CODES for others
        """
        qset = super(ForecastedBalancingAuthorityManager, self).get_query_set()
        if forecast_type == 'any':
            return qset
        else:
            if forecast_type is None:
                forecast_type = 'actual'
            forecast_code = FORECAST_CODES[forecast_type]
            return qset.filter(forecast_code=forecast_code)

    def latest_point(self, forecast_type=None):
        """ Return most recent stored data point for forecast type.
            If multiple with same timestamp, return the most recently extracted.
        """
        try:
            qset = self.get_query_set(forecast_type)
            latest_date = qset.order_by('-date')[0].date
            latest_extracted = qset.filter(date=latest_date).order_by('-date_extracted')[0]
            return latest_extracted
        except:
            return None

    def earliest_point(self, forecast_type=None):
        """ Return oldest stored data point for forecast type.
            If multiple with same timestamp, return the most recently extracted.        
        """
        try:
            qset = self.get_query_set(forecast_type)
            earliest_date = qset.order_by('date')[0].date
            earliest_extracted = qset.filter(date=earliest_date).order_by('-date_extracted')[0]
            return earliest_extracted
        except:
            return None
                    
    def points_in_date_range(self, starttime, endtime, forecast_type=None):
        """ Return all data ponits in the date range for forecast type.
            May include multiple points with same 'date' timestamp.        
        """
        try:
            qset = self.get_query_set(forecast_type)
            points = qset.filter(date__range=(starttime, endtime))
            return points
        except:
            return self.get_query_set().none()

    def best_guess_points_in_date_range(self, starttime, endtime):
        """ Return list of data points for all available timestamps in date range
                using the best available data.
        """
        qset = self.get_query_set().filter(date__range=(starttime, endtime))
        timestamps = sorted(qset.values_list('date', flat=True).distinct())
        return [self.best_guess_point(t) for t in timestamps]

    def best_guess_point(self, timestamp):
        """ Prioritize 'actual' > 'mn_ahead' > 'hr_ahead' > 'dy_ahead' > etc.
            And prioritize most recently extracted data for each forecast type.
        """
        # get all data with timestamp
        qset = self.get_query_set().filter(date=timestamp)

        # if no data, return None
        if qset.count() == 0:
            return self.get_query_set().none()
            
        # if there is data, get the best forecast
        preference_list = ['actual', 'mn_ahead', 'hr_ahead', 'dy_ahead']
        for forecast_type in preference_list:

            # see if there's data for this forecast
            forecast_qset = qset.filter(forecast_code=FORECAST_CODES[forecast_type])
            
            if forecast_qset.count() > 0:
                # get the most recently extracted for forecast
                return forecast_qset.order_by('-date_extracted')[0]
                
