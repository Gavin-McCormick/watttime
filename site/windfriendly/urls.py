from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^status[/]?$',
        'windfriendly.views.status', name='status'),
    url(r'^forecast[/]?$',
        'windfriendly.views.forecast', name='forecast'),
    url(r'^update/(?P<utility>[a-zA-Z0-9_-]+)[/]?$',
        'windfriendly.views.update', name='update'),
    url(r'^history/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        'windfriendly.views.history', name='history'),
  #  url(r'^average/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
  #      'windfriendly.views.average_usage_for_hours', name='average'),
    url(r'^profile[/]',
        'windfriendly.account.views.profile_show', name='profile_show'),
    url(r'^profile/edit[/]',
        'windfriendly.account.views.profile_edit', name='profile_edit'),
    url(r'^profile/create[/]', 
        'windfriendly.account.views.profile_create', name='profile_create'),
    url(r'^login[/]',
        'windfriendly.account.views.login', name='login'),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
    url(r'accounts', include('allauth.urls')),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
      'document_root': settings.MEDIA_ROOT,
    }),
  )
