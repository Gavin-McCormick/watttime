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
    url(r'^average/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        'windfriendly.views.average_usage_for_period', name='average'),
    url(r'^signup[/]?$', 
        'windfriendly.accounts.views.profile_create', name='profile_create'),
    url(r'^profile[/](?P<userid>[a-zA-Z0-9_-]+)[/]?', 
        'windfriendly.accounts.views.profile_complete', name='profile_complete'),
    url(r'^welcome/(?P<userid>[a-zA-Z0-9_-]+)[/]?$', 
        'windfriendly.accounts.views.welcome', name='welcome'),
  #  url(r'accounts', include('allauth.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
      'document_root': settings.MEDIA_ROOT,
    }),
  )
