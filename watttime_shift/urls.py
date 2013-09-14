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

from django.conf.urls import patterns, url, include
from tastypie.api import Api
from . import views
from .api import ShiftResource


v1_api = Api(api_name='v1')
v1_api.register(ShiftResource())

# tastypie resource urls
urlpatterns = patterns('',
    (r'^api/', include(v1_api.urls)),
)

# features patterns
urlpatterns += patterns('',
    url(r'^shift[/]$',
        views.shift, name='shift'),
)
