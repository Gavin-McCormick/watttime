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

import allauth
import registration
from django.views.generic.base import TemplateView

from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

# basic patterns
urlpatterns = patterns('',
    url(r'^[/]?$',
        # 'accounts.views.profile_create', name='home'),
        'accounts.views.shut_down', name='home'),
    url(r'^fakeindex[/]?$',
         'accounts.views.profile_create', name='fakehome'),
    url(r'^ping5[/]?$',
        'workers.views.recurring_events', name='ping5'),
    url(r'^demo[/]?$',
        'workers.views.demo', name='demo'),
    url(r'^data_dump/(?P<database>[a-zA-Z0-9_-]+)[/]?$',
        'workers.views.data_dump', name='data_dump'),
    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)

# allauth patterns
urlpatterns += patterns('',
    url(r'accounts[/]',  include('allauth.urls')),
#    url(r'^accounts/profile[/]$', TemplateView.as_view(template_name='account/profile.html')),
    url(r'^accounts/profile[/]$', 'accounts.views.profile_create', name='user_profile'),
    url(r'^login/cancelled[/]$', 'login_cancelled', name='socialaccount_login_cancelled'),
    url(r'^login/error[/]$', 'login_error', name='socialaccount_login_error'),
)

# invitation patterns
urlpatterns += patterns('',
    url(r'accounts[/]',  include('invitation.urls')),
)

# pages patterns
urlpatterns += patterns('pages.views',
    url(r'^faq[/]?$',
        'faq', name='faq'),
    url(r'^contact[/]?$',
        'contact', name='contact'),
    url(r'^contact/thankyou[/]?$',
        'thankyou', name='contact_thank_you'),
    url(r'^about-us[/]?$',
        'about_us', name='about-us'),
    url(r'^how-it-works[/]?$',
        'how_it_works', name='how-it-works'),
    url(r'^terms-of-service[/]?$',
        'terms_of_service', name='terms-of-service'),
    url(r'^status[/]?$',
        'status_offline', name='status'),
	url(r'^NE_status[/]?$',
        'NE_status', name='NE_status'),
	url(r'^CA_status[/]?$',
        'CA_status', name='CA_status'),
	url(r'^BPA_status[/]?$',
        'BPA_status', name='BPA_status'),
    url(r'^facebook_pilot[/]?$',
        'facebook_pilot', name='facebook_pilot'),
    url(r'^sierra_pilot[/]?$',
        'sierra_pilot', name='sierra_pilot'),
)

# accounts patterns
urlpatterns += patterns('accounts.views',
   # url(r'^signup[/]?$', 
   #     'accounts.views.profile_create', name='profile_create'),
    url(r'^phone_setup/(?P<userid>[a-zA-Z0-9_-]+)[/]?',
        'phone_setup', name='phone_setup'),
    url(r'^phone_verify/(?P<userid>[a-zA-Z0-9_-]+)[/]?',
        'phone_verify', name='phone_verify'),
    url(r'^profile/(?P<userid>[a-zA-Z0-9_-]+)[/]?',
        'profile_alpha', name='profile_alpha'),
    url(r'^welcome_alpha[/]?$',
        'welcome_alpha', name='welcome_alpha'),
    url(r'^thanks[/]?$',
        'thanks', name='thanks'),
    url(r'^unsubscribe/(?P<phone>[0-9-]+)[/]?$',
        'unsubscribe', name='unsubscribe'),
)

# windfriendly API patterns
urlpatterns +=  patterns('windfriendly.views',
    url(r'^green[/]?$',
        'green', name='green'),
    url(r'^forecast[/]?$',
        'forecast', name='forecast'),
    url(r'^update/(?P<utility>[a-zA-Z0-9_-]+)[/]?$',
        'update', name='update'),
    url(r'^summarystats[/]?$',
        'summarystats', name='summarystats'),
    url(r'^history[/]?$',
        'history', name='history'),
    url(r'^today[/]?$',
        'today', name='today'),
    url(r'^average/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        'average_usage_for_period', name='average'),
    url(r'^debug[/]?$',
        'debug_messages', name='debug_messages'),
)

# twilio
urlpatterns += patterns('sms_tools.views',
    url(r'twilio_endpoint', 'twilio_endpoint', name='twilio_endpoint'),
)

# static
urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
                        )
