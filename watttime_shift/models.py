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
from django.forms import ModelForm
from django.core.exceptions import ValidationError

class ShiftRequest(models.Model):
    """ Model for storing requests submitted to the WattTime Shift feature """

    # datetime of request, in UTC
    date_created = models.DateTimeField(db_index=True)

    # foreign key of user making request, if one can be gleaned
    # can't use actual ForeignKey because User.id may not be NULL
    requested_by = models.IntegerField(blank=True, null=True)

    # number of hours that user wants to use energy
    USAGE_CHOICES = (
        (1.0, '1'),
        (2.0, '2'),
        (3.0, '3'),
        (4.0, '4'),
        (5.0, '5'),
        (6.0, '6'),
    )
    usage_hours = models.FloatField(choices=USAGE_CHOICES, default=3.0)

    # number of hours in which user can shift usage
    TIME_RANGE_CHOICES = (
        (2.0, '2'),
        (3.0, '3'),
        (4.0, '4'),
        (5.0, '5'),
        (6.0, '6'),
        (7.0, '7'),
        (8.0, '8'),
        (9.0, '9'),
        (10.0, '10'),
        (11.0, '11'),
        (12.0, '12'),
        (13.0, '13'),
        (14.0, '14'),
        (15.0, '15'),
        (16.0, '16')
    )
    time_range_hours = models.FloatField(choices=TIME_RANGE_CHOICES, default=12.0)

    # start time of recommended usage time, in UTC
    recommended_start = models.DateTimeField()

    # average fraction green during recommended usage time
    recommended_fraction_green = models.FloatField()

    # average fraction green during full time period
    baseline_fraction_green = models.FloatField()

    # id of balancing authority in which data was requested
    BA_CHOICES = (
        (0, 'CAISO'),
    )
    ba = models.IntegerField(choices=BA_CHOICES, default=0)

    def clean(self):
        # Don't allow draft entries to have a pub_date.
        if not self.usage_hours < self.time_range_hours:
            raise ValidationError("usage hours %d >= total hours %d" % (self.usage_hours, self.time_range_hours))

class ShiftRequestForm(ModelForm):
    class Meta:
        model = ShiftRequest
        fields = ('usage_hours', 'time_range_hours')
