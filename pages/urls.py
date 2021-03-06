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
from django.views.generic import TemplateView, RedirectView, ListView
from .models import Article, Award
from . import views

# home
urlpatterns = patterns('',
    url(r'^[/]?$',
        views.frontpage, name='home'),
)

# tools
urlpatterns += patterns('',
    url(r'^status[/]$',
        RedirectView.as_view(url='http://api.watttime.org/map/'), name='status'),
    url(r'^alerts/home[/]$',
        TemplateView.as_view(template_name='pages/alerts_home.html'), name='alerts_home'),
    url(r'^windshed[/]$',
        TemplateView.as_view(template_name='pages/windshed.html'), name='windshed'),
)

# tactics
urlpatterns += patterns('',
    url(r'^how-it-works[/]$',
        TemplateView.as_view(template_name='pages/how_it_works.html'), name='how-it-works'),
    url(r'^why-it-works[/]$',
        TemplateView.as_view(template_name='pages/why_it_works.html'), name='why-it-works'),
)

# team
urlpatterns += patterns('',
    url(r'^about-us[/]$',
        ListView.as_view(template_name='pages/about_us.html', model=Award), name='about-us'),
    url(r'^join-us[/]$',
        TemplateView.as_view(template_name='pages/join_us.html'), name='join-us'),
    url(r'^press[/]$',
        ListView.as_view(template_name='pages/press.html', model=Article), name='press'),
    url(r'^partner[/]$',
        TemplateView.as_view(template_name='pages/partner.html'), name='partner'),
)

# other
urlpatterns += patterns('',
    url(r'^placeholder[/]$',
        TemplateView.as_view(template_name='pages/placeholder.html'), name='placeholder'),
    url(r'^faq[/]$',
        TemplateView.as_view(template_name='pages/faq.html'), name='faq'),
    url(r'^contact[/]$',
        views.contact, name='contact'),
    url(r'^contact/thankyou[/]$',
        TemplateView.as_view(template_name='pages/contact_thank_you.html'), name='contact_thank_you'),
    url(r'^terms-of-service[/]$',
        TemplateView.as_view(template_name='pages/terms_of_service.html'), name='terms-of-service'),
    url(r'^privacy[/]$',
        TemplateView.as_view(template_name='pages/privacy-policy.html'), name='privacy'),
)