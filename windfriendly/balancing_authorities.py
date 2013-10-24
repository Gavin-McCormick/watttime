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


from windfriendly.models import BPA, NE, CAISO, MISO, PJM
from windfriendly.parsers import BPAParser, NEParser, CAISOParser, MISOParser, PJMParser

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
    'DE': 'PJM',
    'DC': 'PJM',
   # 'FL': 'Florida',
   # 'GA': 'Georgia',
   # 'HI': 'Hawaii',
    'ID': 'BPA',
    'IL': 'MISO',
    'IN': 'MISO',
    'IA': 'MISO',
   # 'KS': 'Kansas',
    'KY': 'PJM',
   # 'LA': 'Louisiana',
    'ME': 'ISONE',
    'MD': 'PJM',
    'MA': 'ISONE',
    'MI': 'MISO',
    'MN': 'MISO',
   # 'MS': 'Mississippi',
   # 'MO': 'Missouri',
   # 'MT': 'Montana',
    'ND': 'MISO',
   # 'NE': 'Nebraska',
   # 'NV': 'Nevada',
    'NH': 'ISONE',
    'NJ': 'PJM',
   # 'NM': 'New Mexico',
   # 'NY': 'NYISO',
   # 'NC': 'North Carolina',
    'ND': 'MISO',
    'OH': 'PJM',
   # 'OK': 'Oklahoma',
    'OR': 'BPA',
    'PA': 'PJM',
    'RI': 'ISONE',
   # 'SC': 'South Carolina',
    'SD': 'MISO',
   # 'TN': 'Tennessee',
   # 'TX': 'Texas',
   # 'UT': 'Utah',
    'VT': 'ISONE',
    'VA': 'PJM',
    'WA': 'BPA',
    'WV': 'PJM',
    'WI': 'MISO',
   # 'WY': 'Wyoming',
}

BA_MODELS = {
    'BPA': BPA,
    'NE': NE,
    'ISONE': NE,
    'CAISO': CAISO,
    'MISO': MISO,
    'PJM': PJM,
}

BA_PARSERS = {
    'BPA': BPAParser,
    'NE': NEParser,
    'ISONE': NEParser,
    'CAISO': CAISOParser,
    'MISO': MISOParser,
    'PJM': PJMParser,
}
