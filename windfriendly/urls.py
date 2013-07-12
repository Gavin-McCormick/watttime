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
# Authors: Sam Marcellus, Anna Schneider, Kevin Yang

from django.conf.urls import patterns, url
from . import views

# windfriendly API patterns
urlpatterns =  patterns('',
    url(r'^current[/]?$',
        views.current, name='current'),
    url(r'^forecast[/]?$',
        views.forecast, name='forecast'),
    url(r'^update/(?P<utility>[a-zA-Z0-9_-]+)[/]?$',
        views.update, name='update'),
    url(r'^summarystats[/]?$',
        views.summarystats, name='summarystats'),
    url(r'^history[/]?$',
        views.history, name='history'),
    url(r'^today[/]?$',
        views.today, name='today'),
    url(r'^alerts[/]?$',
        views.alerts, name='alerts'),
    url(r'^average/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        views.average_usage_for_period, name='average'),
    url(r'^averageday[/]?$',
        views.averageday, name='averageday'),
    url(r'^debug[/]?$',
        views.debug_messages, name='debug_messages'),
)
