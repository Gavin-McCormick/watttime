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
from django.views.generic import TemplateView
from django.contrib.auth import views as django_views
from . import views

# custom urls
urlpatterns = patterns('',
    url(r'^magic_invite/(?P<email>[a-zA-Z0-9._+@-]+)[/]?$',
        views.http_invite, name='http_invite'),
    url(r'^magic_invite/(?P<email>[a-zA-Z0-9._+@-]+)/(?P<name>[a-zA-Z 0-9._+@-]+)[/]?$',
        views.http_invite_with_name, name='http_invite_with_name'),
    url(r'^profile/(?P<magic_login_code>[0-9]+)[/]?$',
        views.magic_login, name='magic_login'),
    url(r'^authenticate[/]?$',
        views.authenticate_view, name='authenticate'),
    url(r'^login[/]?$',
        views.user_login, name='user_login'),
    url(r'^profile/settings[/]?$',
        views.profile_settings, name='profile_settings'),
    url(r'^profile/create[/]?$',
        views.profile_create, name='profile_create'),
    url(r'^profile/firsttime[/]?$',
        views.profile_first_edit, name='profile_first_edit'),
    url(r'^profile/verify_phone[/]?$',
        views.phone_verify_view, name='phone_verify_view'),
    url(r'^signup[/]?$',
        views.create_user, name='create_user'),
    url(r'^deactivate[/]?$',
        views.deactivate, name='deactivate'),
    url(r'^reactivate[/]?$',
        views.reactivate, name='reactivate'),
    url(r'^signed_up[/]$',
        TemplateView.as_view(template_name='accounts/signed_up.html'), name='signed_up'),
    url(r'^signed_up_future[/]$',
        TemplateView.as_view(template_name='accounts/signed_up_future.html'), name='signed_up_future'),
)

# Django built-in urls
urlpatterns += patterns('',
    url(r'^accounts/password/change[/]$',
        django_views.password_change,
        {'template_name': 'accounts/password_change.html'},
        name='password_change'),
    url(r'^accounts/password/change/done[/]$',
        django_views.password_change_done,
        {'template_name': 'accounts/password_change_done.html'},
        name='password_change_done'),
    url(r'^accounts/password/reset[/]$',
        django_views.password_reset,
        {'template_name': 'accounts/password_reset_form.html', 'email_template_name': 'accounts/password_reset_email.html'},
        name='password_reset'),
    url(r'^accounts/password/reset/(?P<uidb36>[0-9A-Za-z]+)-(?P<token>.+)[/]$',
        django_views.password_reset_confirm,
        {'template_name': 'accounts/password_reset_confirm.html'},
        name='password_reset_confirm'),
    url(r'^accounts/password/reset/complete[/]$',
        django_views.password_reset_complete,
        {'template_name': 'accounts/password_reset_complete.html'},
        name='password_reset_complete'),
    url(r'^accounts/password/reset/done[/]$',
        django_views.password_reset_done,
        {'template_name': 'accounts/password_reset_done.html'},
        name='password_reset_done'),
    url(r'^accounts/logout[/]$',
        django_views.logout, {'next_page':'/'},
        name='logout'),
)