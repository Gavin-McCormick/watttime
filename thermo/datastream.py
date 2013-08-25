import traceback
import datetime
import pytz
import requests
import os
import os.path

base_dir = os.getcwd()

epoch = datetime.datetime(2013, 8, 1, tzinfo = pytz.utc)
def dt_to_str(dt):
    return str((dt - epoch).total_seconds())
def dt_from_str(s):
    return epoch + datetime.timedelta(seconds = float(s))

class InputStream:
    def __init__(self, iso, name):
        self.iso = iso
        self.name = name
        self.data = []
        self.load()

    def filename(self):
        d = os.path.join(base_dir, 'data', self.iso)

        # Python 3 only:
        # os.makedirs(d, exist_ok=True)

        try:
            os.makedirs(d)
        except OSError:
            pass
        return os.path.join(d, self.name)

    def load(self):
        # We assume no data is from the future, as that might mess
        # up the sort when we append data in the future.
        # Oldest data points at the beginning,
        # most recent data points at the end.
        self.data = []
        name = self.filename()
        if os.path.exists(name):
            with open(name, 'r') as f:
                for line in f:
                    a, b = line.split()
                    dt = dt_from_str(a)
                    val = float(b)
                    self.data.append((dt, val))
            self.data.sort()

    def pull_data(self):
        pass

    def refresh(self):
        val = self.pull_data()
        now = datetime.datetime.now(pytz.utc)
        if val is not None:
            with open(self.filename(), 'a') as f:
                f.write('{} {}\n'.format(dt_to_str(now), str(val)))
            self.data.append((now, val))

    def cur_value(self):
        return self.data[-1][1]

    # Returns first index that has a timestamp greater than or equal to 'time'
    def find_index(self, time):
        low = 0
        high = len(self.data)
        while low < high:
            mid = (low + high) // 2

            if self.data[mid][0] < time:
                low = mid + 1
            else:
                high = mid
        return low

    def forget_old_data(self, time):
        self.data = self.data[self.find_index(time):]

class PercentDirty(InputStream):
    def __init__(self, iso):
        InputStream.__init__(self, iso, 'percent_dirty')

    def pull_data(self):
        url1 = 'http://www.watttime.com/api/v1/{iso}/?format=json&limit=1&order_by=-date&forecast_code=0'
        url2 = 'http://www.watttime.com/api/v1/{iso}/?format=json&limit=1&order_by=-date'
        # I wish there was a uniform interface across isos!
        if self.iso in ['isone', 'bpa']:
            urls = [url2.format(iso = self.iso)]
        elif self.iso in ['caiso']:
            urls = [url1.format(iso = self.iso)]
        else:
            raise RuntimeError("Unknown ISO {}?".format(self.iso))

        for url in urls:
            response = requests.get(url)
            if response.status_code == 200:
                json = response.json()
                data_point = json['objects'][0]
                percent_dirty = (100.0 - data_point['percent_green']) / 100.0
                return percent_dirty
        return None
