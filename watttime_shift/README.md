The <code>watttime_shift</code> app implements one of the core functions of WattTime---recommending clean times to use electricity.
There are two ways to access this information:
* at the <code>/shift/</code> URI (code in models.py and views.py)
* RESTful calls to <code>/api/v1/shift/</code> (code in api.py)

In GET requests, filtering is possible on:
* 'reqeusted_by': user id if the user is logged in, null if not
* 'date_created': start time of period in UTC, as YYYY-mm-DDTHH:MM:SS
* 'time_range_hours': number of hours after date_created to examine
* 'usage_hours': length of planned energy use
* 'recommended_fraction_green': the average fraction of clean energy during the recommended usage period
* 'baseline_fraction_green': the average fraction of clean energy during the whole period of time_range_hours
* 'ba': integer code for balancing authority (only supporting 0 for CAISO)

The <code>greenest_subrange</code> view in the windfriendly app is also relevant.

For example:
    '''
    $ curl "http://localhost:8000/greenest_subrange/?st=CA&time_range_hours=12&usage_hours=3"
    {'recommended_start': datetime.datetime(2013, 9, 15, 7, 0, tzinfo=<UTC>), 'recommended_fraction_green': 0.062227287573985268, 'recommended_end': datetime.datetime(2013, 9, 15, 10, 0, tzinfo=<UTC>), 'baseline_fraction_green': 0.058149527336833352, 'date_created': datetime.datetime(2013, 9, 15, 0, 34, 6, 458584, tzinfo=<UTC>)}"
    $ curl --dump-header - -H "Content-Type: application/json" -X POST --data '{"ba": 0, "recommended_start": "2013-09-15T07:00", "recommended_fraction_green": 0.062227287573985268, "baseline_fraction_green": 0.058149527336833352, "date_created": "2013-09-15T00:34:06", "requested_by": null, "time_range_hours": 12.0, "usage_hours": 3.0}' http://localhost:8000/api/v1/shift/
    HTTP/1.0 201 CREATED
    Date: Sun, 15 Sep 2013 00:42:26 GMT
    Server: WSGIServer/0.1 Python/2.7.4
    Vary: Accept
    Content-Type: text/html; charset=utf-8
    Location: http://localhost:8000/api/v1/shift/20/
    $ curl -H "Content-Type: application/json" "http://localhost:8000/api/v1/shift/?recommended_fraction_green__gt=0.062&order_by=-date_created"
    {"meta": {"limit": 20, "next": null, "offset": 0, "previous": null, "total_count": 6}, "objects": [{"ba": 0, "baseline_fraction_green": 0.05814952733683335, "date_created": "2013-09-15T00:34:06", "id": 20, "recommended_fraction_green": 0.06222728757398527, "recommended_start": "2013-09-15T07:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/20/", "time_range_hours": 12.0, "usage_hours": 3.0}, {"ba": 0, "baseline_fraction_green": 0.05814952733683335, "date_created": "2013-09-15T00:34:06", "id": 21, "recommended_fraction_green": 0.06222728757398527, "recommended_start": "2013-09-15T07:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/21/", "time_range_hours": 12.0, "usage_hours": 3.0}, {"ba": 0, "baseline_fraction_green": 0.05802832112163617, "date_created": "2013-07-20T19:56:18.185978", "id": 17, "recommended_fraction_green": 0.0668057774710331, "recommended_start": "2013-07-21T04:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/17/", "time_range_hours": 12.0, "usage_hours": 3.0}, {"ba": 0, "baseline_fraction_green": 0.055089480646464156, "date_created": "2013-07-20T18:06:16.484399", "id": 16, "recommended_fraction_green": 0.06257416348156127, "recommended_start": "2013-07-21T03:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/16/", "time_range_hours": 12.0, "usage_hours": 3.0}, {"ba": 0, "baseline_fraction_green": 0.055089480646464156, "date_created": "2013-07-20T18:03:23.716146", "id": 14, "recommended_fraction_green": 0.06257416348156127, "recommended_start": "2013-07-21T03:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/14/", "time_range_hours": 12.0, "usage_hours": 3.0}, {"ba": 0, "baseline_fraction_green": 0.055089480646464156, "date_created": "2013-07-20T18:00:12.293880", "id": 13, "recommended_fraction_green": 0.06257416348156127, "recommended_start": "2013-07-21T03:00:00", "requested_by": null, "resource_uri": "/api/v1/shift/13/", "time_range_hours": 12.0, "usage_hours": 3.0}]}
    '''


