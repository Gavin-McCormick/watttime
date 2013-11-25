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

from django.views.generic.base import TemplateView

from django.conf.urls import patterns, url, include
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# basic patterns
urlpatterns = patterns('',
  #  url(r'^data_text/(?P<database>[a-zA-Z0-9_-]+)[/]?$',
  #      'workers.views.data_text_view', name='data_text'),
  #  url(r'^data_json/(?P<database>[a-zA-Z0-9_-]+)[/]?$',
  #      'workers.views.data_json_view', name='data_json'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

#  allauth patterns
#urlpatterns += patterns('',
#    url(r'accounts[/]',  include('allauth.urls')),
#    url(r'^accounts/profile[/]$', TemplateView.as_view(template_name='account/profile.html')),
#    url(r'^accounts/profile[/]$', 'accounts.views.profile_create', name='user_profile'),
#    url(r'^login/cancelled[/]$', 'login_cancelled', name='socialaccount_login_cancelled'),
#    url(r'^login/error[/]$', 'login_error', name='socialaccount_login_error'),
#)

# invitation patterns
#urlpatterns += patterns('',
#    url(r'accounts[/]',  include('invitation.urls')),
#)

# tools patterns
urlpatterns += patterns('',
    url(r'',  include('watttime_shift.urls')),
)

# pages patterns
urlpatterns += patterns('',
    url(r'',  include('pages.urls')),
)

handler500 = 'pages.views.server_error'
handler404 = 'pages.views.notfound_error'

# accounts patterns
urlpatterns += patterns('',
    url(r'', include('accounts.urls')),
)

# windfriendly API patterns
urlpatterns += patterns('',
    url(r'',  include('windfriendly.urls')),
)

# twilio
urlpatterns += patterns('sms_tools.views',
    url(r'twilio_endpoint', 'twilio_endpoint', name='twilio_endpoint'),
)

# static
urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
                        )
