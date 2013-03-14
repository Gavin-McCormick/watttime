import urllib2
import dateutil.parser as dp
from windfriendly.models import BPA


class UtilityParser():
    pass

class BPAParser(UtilityParser):
    def __init__(self):
        self.BPA_LOAD_URL = 'http://transmission.bpa.gov/business/operations/wind/baltwg.txt'
        self.BPA_LOAD_NCOLS = 5
        self.BPA_LOAD_SKIP_LINES = 7

        self.BPA_OVERSUPPLY_URL = 'http://transmission.bpa.gov/business/operations/wind/twndbspt.txt'
        self.BPA_OVERSUPPLY_NCOLS = 4
        self.BPA_OVERSUPPLY_SKIP_LINES = 11

    def getData(self, url):
        # Make request for data
        try:
            data = urllib2.urlopen(url).read()
        except urllib2.HTTPError, e:
            raise Exception('unable to get BPA data' + str(e))
        return data


    def parseDate(self, datestring):
        tzd = {
            'PST': -28800,
            'PDT': -25200,
        }
        try:return dp.parse(datestring, tzinfos=tzd)
        except: raise Exception(datestring)


    def parseLoadRow(self, row):
        fields = row.split('\t')
        res = {'date': self.parseDate(fields[0])}
        if len(fields) == 5:
            [total, wind, hydro, thermal]  = [int(x) for x in fields[1:]]
            res.update({'wind': wind, 'hydro': hydro, 'thermal': thermal,
                        'total': total})
            return res
        else:
            return res

    def parseOversupplyRow(self, row):
        fields = row.split('\t')
        res = {'date': self.parseDate(fields[0])}
        if len(fields) == 4:
            [basepoint, wind, oversupply] = [int(x) for x in fields[1:]]
            res.update({'basepoint': basepoint, 'wind': wind,
                        'oversupply': oversupply})
            return res
        else:
            return res

    def rowIsAfterDate(self, row, date):
        row_date = row['date']
        return row_date > date

    def rowHasAllCols(self, row, ncols):
        return len(row) == ncols

    def isGoodRow(self, row, ncols, date=None):
        if date:
            return (self.rowHasAllCols(row, ncols) and self.rowIsAfterDate(row, date))
        else:
            return self.rowHasAllCols(row, ncols)

    def parse(self, url, parse_row_fn, skip_lines, ncols, latest_date=None):
        data = self.getData(url)
        # First skip_lines lines are boilerplate text, last line is blank
        rows = data.split('\r\n')[skip_lines:-1]
        parsed_rows = [parse_row_fn(row) for row in rows]
        res = filter(lambda x: self.isGoodRow(x, ncols, latest_date), parsed_rows)
        return res

    def parseBPALoad(self, latest_date=None):
        return self.parse(self.BPA_LOAD_URL, self.parseLoadRow,
                     self.BPA_LOAD_SKIP_LINES, self.BPA_LOAD_NCOLS,
                     latest_date)

    def parseBPAOversupply(self, latest_date=None):
        return self.parse(self.BPA_OVERSUPPLY_URL, self.parseOversupplyRow,
                     self.BPA_OVERSUPPLY_SKIP_LINES, self.BPA_OVERSUPPLY_NCOLS,
                     latest_date)

    def zipTables(self, table_a, table_b):
        max_index = reduce(min, map(len, [table_a, table_b]))
        res = []
        for i in xrange(max_index):
            res.append(dict(table_a[i].items() + table_b[i].items()))
        return res

    def getBPA(self, latest_date=None):
        parsed_load = self.parseBPALoad(latest_date)
        parsed_oversupply = self.parseBPAOversupply(latest_date)
        return self.zipTables (parsed_load, parsed_oversupply)

    def writeBPA(self, row):
        b = BPA()
        b.date = row['date']
        b.load = row['total']
        b.wind = row['wind']
        b.hydro = row['hydro']
        b.thermal = row['thermal']
        b.save()

    def update(self, latest_date=None):
        update = self.getBPA (latest_date)
        for row in update:
            self.writeBPA(row)

    def periodicUpdateBPA(self):
        raw = BPA.objects.latest('date')
        self.update(raw)
