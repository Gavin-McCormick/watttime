Overview
----------
<code>windfriendly</code> is a reusable (i.e., standalone) app that handles scraping, processing, and retrieving functionality
for renewable energy generation data from Independent System Operators (ISOs) and other balancing authorities (BAs).

Currently, several BAs are supported:
* CAISO: California
* BPA: Washington, Oregon, Idaho
* ISONE: Massachusetts, Maine, Vermont, New Hampshire, Connecticut, Rhode Island
* MISO: much of the Midwest and Great Lakes
* PJM: mid-Atlantic states from Pennsylvania to Virgina, including DC

In this app, each BA is associated with:
* a parser that scrapes the data (in <code>parsers.py</code>)
* a model that stores the data (in <code>models.py</code>, with custom managers and querysets in <code>managers.py</code>)
* API resources for retrieving the data (in <code>api.py</code> and <code>views.py</code>, with URLs in <code>urls.py</code>)
* tests (in <code>tests/</code>) and test fixtures (in <code>fixtures/</code>)
* other constants (in <code>balancing_authorities.py</code> and <code>settings.py</code>)


Usage: Standard JSON API
---------------
The standard JSON API is built with [Tastypie](http://django-tastypie.readthedocs.org/) and has the base URI

    /api/v1/[BA_NAME]/?format=json

where <code>[BA_NAME]</code> is one of 'caiso', 'bpa', 'isone', 'miso', or 'pjm'.

The following filters are available:
* limit: default is one day's worth of data
* date: in ISO format (YYYY-mm-DDT%H:%M:%S.%LZ)
* order_by: 'date' for earliest-first ordering, '-date' for latest-first ordering
* forecast_code: 0 for actual data, 1 for forecast
* marginal_fuel: index of the fuel name in this list: ['Coal', 'Oil', 'Natural Gas', 'Refuse', 'Hydro', 'Wood', 'Nuclear', 'Solar', 'Wind', 'None']. For example, oil is 1 and wind is 8. This data is only available for ISONE, so marginal_fuel is None for all other regions.

For example, to get the most recent data point in BPA:

    /api/v1/bpa/?format=json&order_by=-date&limit=1

    {
	  "meta": {
	    "limit": 1, 
	    "next": "/api/v1/bpa/?offset=1&order_by=-date&format=json&limit=1", 
	    "offset": 0, 
	    "previous": null, 
	    "total_count": 64721
	  }, 
	  "objects": [
	    {
	      "date": "2014-02-04T18:25:00+00:00", 
	      "date_extracted": "2014-02-04T18:33:18+00:00", 
	      "forecast_code": 0, 
	      "fraction_clean": 0.084051724137931, 
	      "local_date": "2014-02-04T10:25:00-08:00", 
	      "marginal_fuel": 9, 
	      "resource_uri": "/api/v1/bpa/64721/", 
	      "total_MW": 12992.0
	    }
	  ]
	}

Or to get 4 hours of day-ahead-forecast data from CAISO on October 1 (note that the date range is inclusive and times are in UTC):

    /api/v1/caiso/?format=json&order_by=date&date__range=2013-10-01T00:00,2013-10-01T03:00&forecast_code=1

    {
	  "meta": {
	    "limit": 24, 
	    "next": null, 
	    "offset": 0, 
	    "previous": null, 
	    "total_count": 4
	  }, 
	  "objects": [
	    {
	      "date": "2013-10-01T00:00:00+00:00", 
	      "date_extracted": "2013-09-30T23:10:19+00:00", 
	      "forecast_code": 1, 
	      "fraction_clean": 0.0862876245793019, 
	      "local_date": "2013-09-30T17:00:00-07:00", 
	      "marginal_fuel": 9, 
	      "resource_uri": "/api/v1/caiso/54148/", 
	      "total_MW": 31899.36
	    }, 
	    {
	      "date": "2013-10-01T01:00:00+00:00", 
	      "date_extracted": "2013-09-30T23:10:19+00:00", 
	      "forecast_code": 1, 
	      "fraction_clean": 0.0737352245189512, 
	      "local_date": "2013-09-30T18:00:00-07:00", 
	      "marginal_fuel": 9, 
	      "resource_uri": "/api/v1/caiso/54149/", 
	      "total_MW": 31597.11
	    }, 
	    {
	      "date": "2013-10-01T02:00:00+00:00", 
	      "date_extracted": "2013-09-30T23:10:19+00:00", 
	      "forecast_code": 1, 
	      "fraction_clean": 0.0608385181897262, 
	      "local_date": "2013-09-30T19:00:00-07:00", 
	      "marginal_fuel": 9, 
	      "resource_uri": "/api/v1/caiso/54150/", 
	      "total_MW": 31360.56
	    }, 
	    {
	      "date": "2013-10-01T03:00:00+00:00", 
	      "date_extracted": "2013-09-30T23:10:19+00:00", 
	      "forecast_code": 1, 
	      "fraction_clean": 0.0602227973514438, 
	      "local_date": "2013-09-30T20:00:00-07:00", 
	      "marginal_fuel": 9, 
	      "resource_uri": "/api/v1/caiso/54151/", 
	      "total_MW": 32112.59
	    }
	  ]
	}


Usage: API calls in views
------------------------
In addition, there are a few other URIs that return JSON data in response to a GET request. These are implemented as Django views for now because they're a bit trickier to fold into the tastypie framework, but they should be incorporated eventually. Be prepared to change code that depends on these.

Here are the cheat sheet versions:
* scrape new data and a get a summary of what changed: <code>/update/[BA_NAME]</code>
* get "best guess" data (actual data or most recent forecast data) between 12AM today and 12AM tomorrow in the BA's local time: <code>/today/?st=[ST]</code>
* get an average day of data by aggregating the historical period by hour (e.g., the hour 14 data is the average of the data on each day at 2PM): <code>/averageday/?st=[ST]&start=[YYYYmmDDHHSS]&end=[YYYYmmDDHHSS]</code>
* get max and min alerts for the historical period: <code>/alerts/?st=[ST]&start=[YYYYmmDDHHSS]&end=[YYYYmmDDHHSS]</code>
* get the greenest subrange of length <code>usage_hours</code> out of the next <code>time_range_hours</code> (to be used with the watttime_shift app): <code>/greenest_subrange/?st=[ST]&time_range_hours=[float]&usage_hours=[float]</code>

All start and end date-time arguments are optional and are in UTC. Use the two-letter state code in <code>st=[ST]</code>, or replace with <code>ba=[BA_NAME]</code>.


Usage: Django models
---------------------
Each row for each BA has the following attributes:
* date: date-time of the observation, in UTC
* local_date: date-time of the observation, in the BA's local time
* date_extracted: date-time at which the data was scraped, in UTC (currently only for CAISO)
* total_load: total electricity generation in megawatts
* fraction_green: the fraction of electricity generation from "green" sources (wind, solar, etc)
* fraction_high_carbon: the fraction of electricity generation from "dirty" sources (coal, etc)
* marginal_fuel: an integer code for which fuel is on margin (defined in <code>settings.py</code>)
* forecast_code: an integer code for the forecast type (actual, day-ahead, etc) (defined in <code>settings.py</code>)

Some of these attributes are implemented as database fields and some as properties, and which are which may change in the future; try to avoid depending on this aspect of the implementation where possible. In addition, each model has fields for the specific fuel types that we can find data for; this aspect of the interface is unlikely to become standardized between BAs any time soon.

In addition to Django's Manager and QuerySet methods, the following additional methods are available:
* qs.latest() and qs.earliest() return the row with the latest or earliest value of the date field, as usual, but use the date_extracted field to resolve conflicts
* qs.best_guess_points() returns a list (not a QuerySet, sorry!) of the "best guess" data: unique on date field, using most recently extracted actual data, then most recently extracted forecast data (this logic is in qs.best_guess())
* objects.greenest_subrange(starttime, endtime, timedelta, forecast_type) identifies the contiguous time period of length timedelta within the date range (starttime, endtime) with the highest average fraction_green attribute


TODOs
-------------
An unordered list.
* Build equivalents to "today" and "averageday" views into standard API
* Refactor BPAParser to make its interface more like other parsers
* Change "update" view and parsers to take date arguments to allow easier backfilling of data (maybe using POST requests)
* Make qs.best_guess_points() return QuerySet not list
