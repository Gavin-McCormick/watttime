# BPA parser
import urllib2
import dateutil.parser as dp
from windfriendly.models import BPA

# SETTINGS

BPA_LOAD_URL = 'http://transmission.bpa.gov/business/operations/wind/baltwg.txt'
BPA_LOAD_NCOLS = 5
BPA_LOAD_SKIP_LINES = 7

BPA_OVERSUPPLY_URL = 'http://transmission.bpa.gov/business/operations/wind/twndbspt.txt'
BPA_OVERSUPPLY_NCOLS = 4
BPA_OVERSUPPLY_SKIP_LINES = 11

# TODO package this in a class

def getData (url):
    # Make request for data
    try:
        data = urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        raise Exception('unable to get BPA data' + str(e))
    return data

def parseIntoRows(data):
    return data.split('\r\n')

def parseDate(datestring):
    tzd = {
        'PST': -28800,
        'PDT': -25200,
    }
    return dp.parse(datestring, tzinfos=tzd)


def parseLoadRow(row):
    fields = row.split('\t')
    res = {'date': parseDate(fields[0])}
    if len(fields) == 5:
        [total, wind, hydro, thermal]  = [int(x) for x in fields[1:]]
        res.update({'wind': wind, 'hydro': hydro, 'thermal': thermal,
                    'total': total})
        return res
    else:
        return res

def parseOversupplyRow(row):
    fields = row.split('\t')
    res = {'date': parseDate(fields[0])}
    if len(fields) == 4:
        [basepoint, wind, oversupply] = [int(x) for x in fields[1:]]
        res.update({'basepoint': basepoint, 'wind': wind,
                    'oversupply': oversupply})
        return res
    else:
        return res

def rowIsAfterDate(row, date):
    row_date = row['date']
    return row_date > date

def rowHasAllCols(row, ncols):
    return len(row) == ncols

def isGoodRow(row, ncols, date=None):
    if date:
        return (rowHasAllCols(row, ncols) and rowIsAfterDate(row, date))
    else:
        return rowHasAllCols(row, ncols)

def parse(url, parse_row_fn, skip_lines, ncols, latest_date=None):
    data = getData(url)
    # First skip_lines lines are boilerplate text, last line is blank
    rows = parseIntoRows(data)[skip_lines:-1]
    parsed_rows = [parse_row_fn(row) for row in rows]
    res = filter(lambda x: isGoodRow(x, ncols, latest_date), parsed_rows)
    return res

def parseBPALoad (latest_date=None):
    return parse(BPA_LOAD_URL, parseLoadRow,
                 BPA_LOAD_SKIP_LINES, BPA_LOAD_NCOLS,
                 latest_date)

def parseBPAOversupply (latest_date=None):
    return parse(BPA_OVERSUPPLY_URL, parseOversupplyRow,
                 BPA_OVERSUPPLY_SKIP_LINES, BPA_OVERSUPPLY_NCOLS,
                 latest_date)

def zipTables (table_a, table_b):
    max_index = reduce(min, map(len, [table_a, table_b]))
    res = []
    for i in xrange(max_index):
        res.append(dict(table_a[i].items() + table_b[i].items()))
    return res

def getBPA (latest_date=None):
    parsed_load = parseBPALoad(latest_date)
    parsed_oversupply = parseBPAOversupply(latest_date)
    return zipTables (parsed_load, parsed_oversupply)

def writeBPA (row):
    b = BPA()
    b.date = row['date']
    b.load = row['total']
    b.wind = row['wind']
    b.hydro = row['hydro']
    b.thermal = row['thermal']
    b.save()

def updateBPA (latest_date=None):
    update = getBPA (latest_date)
    for row in update:
        writeBPA(row)

def periodicUpdateBPA():
    raw = BPA.objects.latest('date')
    updateBPA(raw)
