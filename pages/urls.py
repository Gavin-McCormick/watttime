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

urlpatterns = patterns('',
    url(r'^faq[/]?$',
        views.faq, name='faq'),
    url(r'^signed_up[/]?$',
        views.signed_up, name='signed_up'),
    url(r'^signed_up_future[/]?$',
        views.signed_up_future, name='signed_up_future'),
    url(r'^contact[/]?$',
        views.contact, name='contact'),
    url(r'^contact/thankyou[/]?$',
        views.thankyou, name='contact_thank_you'),
    url(r'^about-us[/]?$',
        views.about_us, name='about-us'),
    url(r'^how-it-works[/]?$',
        views.how_it_works, name='how-it-works'),
    url(r'^terms-of-service[/]?$',
        views.terms_of_service, name='terms-of-service'),
    url(r'^status[/]?$',
        views.status, name='status'),
    url(r'^NE_status[/]?$',
        views.NE_status, name='NE_status'),
    url(r'^CA_status[/]?$',
        views.CA_status, name='CA_status'),
    url(r'^BPA_status[/]?$',
        views.BPA_status, name='BPA_status'),
    url(r'^facebook_pilot[/]?$',
        views.facebook_pilot, name='facebook_pilot'),
    url(r'^sierra_pilot[/]?$',
        views.sierra_pilot, name='sierra_pilot'),
)