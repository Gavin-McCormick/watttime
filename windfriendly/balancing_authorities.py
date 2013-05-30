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


from windfriendly.models import BPA, NE, CAISO

# BALANCING_AUTHORTIES is a dict that maps state 2-letter abbrevs to balancing authority abbrevs
# BA_MODELS is a dict that maps balancing authoriy abbrevs to models in models.py

BALANCING_AUTHORITIES = {
   # 'AL': 'Alabama',
   # 'AK': 'Alaska',
   # 'AZ': 'Arizona',
   # 'AR': 'Arkansas',
    'CA': 'CAISO',
   # 'CO': 'Colorado',
    'CT': 'ISONE',
   # 'DE': 'Delaware',
   # 'DC': 'District of Columbia',
   # 'FL': 'Florida',
   # 'GA': 'Georgia',
   # 'HI': 'Hawaii',
    'ID': 'BPA',
   # 'IL': 'Illinois',
   # 'IN': 'Indiana',
   # 'IA': 'Iowa',
   # 'KS': 'Kansas',
   # 'KY': 'Kentucky',
   # 'LA': 'Louisiana',
    'ME': 'ISONE',
   # 'MD': 'Maryland',
    'MA': 'ISONE',
   # 'MI': 'Michigan',
   # 'MN': 'Minnesota',
   # 'MS': 'Mississippi',
   # 'MO': 'Missouri',
   # 'MT': 'Montana',
   # 'NE': 'Nebraska',
   # 'NV': 'Nevada',
    'NH': 'ISONE',
   # 'NJ': 'New Jersey',
   # 'NM': 'New Mexico',
   # 'NY': 'NYISO',
   # 'NC': 'North Carolina',
   # 'ND': 'North Dakota',
   # 'OH': 'Ohio',
   # 'OK': 'Oklahoma',
    'OR': 'BPA',
   # 'PA': 'Pennsylvania',
    'RI': 'ISONE',
   # 'SC': 'South Carolina',
   # 'SD': 'South Dakota',
   # 'TN': 'Tennessee',
   # 'TX': 'Texas',
   # 'UT': 'Utah',
    'VT': 'ISONE',
   # 'VA': 'Virginia',
    'WA': 'BPA',
   # 'WV': 'West Virginia',
   # 'WI': 'Wisconsin',
   # 'WY': 'Wyoming',
}

BA_MODELS = {
    'BPA': BPA,
    'ISONE': NE,
    'CAISO': CAISO,
}
