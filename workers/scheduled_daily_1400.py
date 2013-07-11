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

# set up script to be run from command line
import os
import sys
path = os.path.normpath(os.path.join(os.getcwd(), '..'))
sys.path.append(path)
from django.core.management import setup_environ
import settings
setup_environ(settings)

from workers.tasks import run_daily_tasks_1400

run_daily_tasks_1400()
