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
# Authors: Sam Marcellus, Anna Schneider


# utilities for combining meter reading and balancing authority data

def min_date(meter_qset, ba_qset):
  """ Returns the earliest date with both BA and user meter data """
  min_for_user = meter_qset.order_by('start')[0].start
  min_for_ba = ba_qset.order_by('date')[0].date
  return max(min_for_user, min_for_ba)

def max_date(meter_qset, ba_qset):
  """ Returns the latest date with both BA and user meter data """
  max_for_user = meter_qset.latest('start').start
  max_for_ba = ba_qset.latest('date').date
  return min(max_for_user, max_for_ba)

def ba_rows_for_meter_row(meter_row, ba_qset):
  # get BA rows for user meter row
  start = meter_row.start
  end = meter_row.start + timedelta(0,meter_row.duration)
  rows = ba_qset.filter(date__range=(start, end))

  # get nearby values if none in range
#  if rows.count() == 0:
#    print start, end
#    rows = ba_qset.filter(date__lt=start).latest('date')
#    if len(rows) == 0:
#      rows = [ba_qset.filter(date__gt=end).order_by('date')[0]]

  # return
  return rows
  
def used_green_kwh(meter_row, ba_qset):
  ba_rows = ba_rows_for_meter_row(meter_row, ba_qset)
  try:
    n_rows = float(len(ba_rows))
  except:
    return 0.0

  try:
    fraction_load = sum([row.fraction_clean for row in ba_rows]) / n_rows
  except ZeroDivisionError:
    return 0.0

  return meter_row.total_kwh() * fraction_load


