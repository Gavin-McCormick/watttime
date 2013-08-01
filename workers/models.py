# Copyright wattTime 2013
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Authors: Anna Schneider

from django.db import models
import datetime
import pytz

# KeyValue usage:
#
#   To store something:
#       store(key, value)
#   To get it back later:
#       value = load(key)
#   This returns None if no value was associated with key. The value of 'value'
#   must be of one of the following types:
#       int, str, float, datetime
#   It is the users' responsbility to make sure that key names do not collide,
#   as they are global across the program.
#
#   Key names currently in use, by app:
#   accounts: (none)
#   windfriendly: (none)
#   workers: (none)
# Intended to be used for single variables whose values need to be stored
# persistently. The database does not perform any indexing, so it searches
# sequentially on each load and store.

# Really should be doing this whole thing with pickle or something, but:
#   * Django doesn't have a field type for binary data (maybe TextField
#       can store binary data, but Django's documentation is painfully
#       sparse and it's probably dependent on the SQL backend anyhow)
#   * bytes vs. str isn't fixed until python 3
#   * pickle isn't combined with cPickle until python 3, hurting portability
# Also, I dearly wish I weren't using SQL   /rant  --ems
class KeyValue(models.Model):
    _integer = 0
    _string = 1
    _float = 2
    _datetime = 3
    value_types = [
        (_integer, 'Integer'),
        (_string, 'String'),
        (_float, 'Float'),
        (_datetime, 'Datetime')]

    key = models.TextField(unique = True)
    value = models.TextField(blank = True, default = '')
    # 'type' in Italian, as 'type' is a keyword in python
    tipo = models.IntegerField(choices = value_types, default = 0)

    def __unicode__(self):
        return u'{}: {}'.format(self.key, str(self.value))

# The value of the epoch doesn't matter so long as it is never changed,
# as datetimes are stored relative to this epoch
_epcoh = datetime.datetime(2000, 1, 1, tzinfo = pytz.utc)

def store(key, value):
    kvs = list(KeyValue.objects.filter(key = key))
    if len (kvs) == 0:
        kv = KeyValue()
        kv.key = key
    else:
        kv = kvs[0]

    if isinstance(value, int):
        kv.tipo = KeyValue._integer
        kv.value = str(value)
    elif isinstance(value, str):
        kv.tipo = KeyValue._string
        kv.value = value
    elif isinstance(value, float):
        kv.tipo = KeyValue._float
        kv.value = str(value)
    elif isinstance(value, datetime.datetime):
        kv.tipo = KeyValue._datetime
        kv.value = str((value - _epoch).total_seconds())
    else:
        raise ValueError("Cannot store item {!s} of unknown type {!s}.".
                format(value, type(value)))
    kv.save()

# Returns None in case that key was missing in database
def load(key):
    kvs = list(KeyValue.objects.filter(key = key))
    if len(kvs) == 0:
        return None

    kv = kvs[0]
    if kv.tipo == KeyValue._integer:
        return int(kv.value)
    elif kv.tipo == KeyValue._string:
        return kv.value
    elif kv.tipo == KeyValue._float:
        return float(kv.value)
    elif kv.tipo == KeyValue._datetime:
        return _epoch + datetime.timedelta(seconds = float(kv.value))
    else:
        raise RuntimeError("Unknown data type {} in KeyValue".format(kv.tipo))

def keys():
    ks = []
    for kv in KeyValue.objects.all():
        ks.append(kv.key)
    return ks

# Given an interval in seconds, print it nicely.
def format_time_interval(interval):
    i = interval

    days = i // (24 * 60 * 60)
    i -= days * 24 * 60 * 60
    hours = i // (60 * 60)
    i -= hours * 60 * 60
    minutes = i // 60
    i -= minutes * 60
    seconds = i

    if days != 0:
        if hours == 0:
            return '{:d} days'.format(days)
        else:
            return '{:d} days {:d} hours'.format(days, hours)
    elif hours != 0:
        if minutes == 0:
            return '{:d} hours'.format(hours)
        else:
            return '{:d} hours {:d} minutes'.format(hours, minutes)
    elif minutes != 0:
        if seconds == 0:
            return '{:d} minutes'.format(minutes)
        else:
            return '{:d} minutes {:d} seconds'.format(minutes, seconds)
    else:
        return '{:d} seconds'.format(seconds)

class ScheduledTasks(models.Model):
    date = models.DateTimeField()
    command = models.TextField()
    repeat = models.BooleanField(default = False)
    repeat_interval = models.IntegerField(default = 60 * 60 * 24)

    def __unicode__(self):
        if self.repeat:
            res = u'{self.dat}: {self.command} (repeats every {itv})'
        else:
            res = u'{self.date}: {self.command}'
        itv = format_time_interval(self.repeat_interval)
        return res.format(self = self, itv = itv)

class DailyReport(models.Model):
    date = models.DateTimeField()
    message = models.TextField()

    def __unicode__(self):
        res = u'{self.date}: {self.message}'
        return res.format(self = self)

class DebugMessage(models.Model):
    date = models.DateTimeField()
    message = models.TextField()

    def __unicode__(self):
        res = u'{self.date}: {self.message}'
        return res.format(self = self)


# TODO switch to using KeyValue
class LastMessageSent(models.Model):
    NE_dirty_daytime = 0
    NE_dirty_evening = 1
    NE_clean = 2

    message_choices = [
            (NE_dirty_daytime, 'ne_dirty_daytime'),
            (NE_dirty_evening, 'ne_dirty_evening'),
            (NE_clean, 'ne_clean')]

    category = models.IntegerField(default = 0, choices = message_choices)
    date = models.DateTimeField()

    def __unicode__(self):
        res = u'{self.category}:    {self.date}'
        return res.format(self = self)

def latest_by_category(c):
    last = None
    for x in LastMessageSent.objects.filter(category = c):
        if last is None or x.date > last.date:
            last = x
    return last
