import traceback
import time
import datetime
import pytz
import requests
import sys
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
        os.makedirs(d, exist_ok=True)
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
    def binary_search(self, time):
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
        self.data = self.data[self.binary_search(time):]

class PercentDirty(InputStream):
    def __init__(self, iso):
        InputStream.__init__(self, iso, 'percent_dirty')

    def pull_data(self):
        url1 = 'http://www.watttime.com/api/v1/{iso}/?format=json&limit=1&order_by=-date&forecast_code=0'
        url2 = 'http://www.watttime.com/api/v1/{iso}/?format=json&limit=1&order_by=-date'
        # for url in [url1, url2]:
        for url in [url2]:
            response = requests.get(url.format(iso = self.iso))
            if response.status_code == 200:
                json = response.json()
                data_point = json['objects'][0]
                percent_dirty = (100.0 - data_point['percent_green']) / 100.0
                return percent_dirty
        return None

class Config:
    def __init__(self, stream, temps):
        self.stream = stream

        temps = temps[:]
        temps.sort()

        total_weight = 0
        for temp in temps:
            total_weight += temp[1]

        weight = 0
        self.temps = []
        for temp in temps:
            weight += temp[1]
            self.temps.append((weight / total_weight, temp[0]))

if __name__ == "__main__":
    def fail(xs, print_exc = False):
        if print_exc:
            traceback.print_exc()
            print ('')

        for x in xs:
            print (x)

        sys.exit(1)

    try:
        import config
    except ImportError:
        fail(["Require a configuration file called 'config.py'."], True)

    try:
        from config import iso, temps
    except ImportError:
        fail(["File 'config.py' must define variables 'iso' and 'temps'.",
            "Example file:",
            "    iso = 'isone'",
            "    temps = [(72, .8), (80, .2)]"], True)

    gzero = False
    for temp in temps:
        if temp[1] < 0:
            fail (["Can't specify a negative frequency '{!s}'".format(temp[1])])
        if temp[1] > 0:
            gzero = True
    if not gzero:
        fail(["Must specify at least one temperature with positive frequency."])

    suppoted_isos = ['isone', 'caiso', 'bpa']
    if not (iso.lower() in suppoted_isos):
        fail(["Unknown ISO '{}'".format(iso),
            "Supported ISOs are: {}".format(', '.join(suppoted_isos))], True)

    config = Config(PercentDirty(iso.lower()), temps)

    oneweek = datetime.timedelta(days = 7)

    while True:
        try:
            config.stream.refresh()

            cur = config.stream.cur_value()

            now = datetime.datetime.now(pytz.utc)
            oneweekago = now - oneweek

            i0 = config.stream.binary_search(oneweekago)
            i1 = len(config.stream.data)
            amount_lower = 0
            amount_greater = 0

            for i in range(i0, i1):
                j = i + 1
                then, value = config.stream.data[i]

                if j == i1:
                    diff = now - then
                else:
                    diff = config.stream.data[j][0] - then

                if diff > datetime.timedelta(hours = 1):
                    diff = datetime.timedelta(hours = 1)

                if value <= cur:
                    amount_lower += diff.total_seconds()
                else:
                    amount_greater += diff.total_seconds()

            percentile = amount_lower / (amount_lower + amount_greater)

            print ("     currently {:.3f} badness, {:.3f} percentile".format(cur, percentile))

            for weight, temp in config.temps:
                if percentile <= weight:
                    print ("[{} UTC] set temperature = {}".format(
                        now.strftime('%H.%M'), temp))
                    break

        except:
            traceback.print_exc()

        time.sleep(5 * 60)
