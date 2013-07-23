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

class ScheduledTasks(models.Model):
    date = models.DateTimeField()
    command = models.CharField(max_length=300)

    def __unicode__(self):
        res = u'{self.date}: {self.command}'
        return res.format(self = self)

class DailyReport(models.Model):
    date = models.DateTimeField()
    # message = models.CharField(max_length=300)
    message = models.TextField()

    def __unicode__(self):
        res = u'{self.date}: {self.message}'
        return res.format(self = self)

class DebugMessage(models.Model):
    date = models.DateTimeField()
    # message = models.CharField(max_length=300)
    message = models.TextField()

    def __unicode__(self):
        res = u'{self.date}: {self.message}'
        return res.format(self = self)

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
