from django.conf.urls.defaults import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^status[/]?$', 'windfriendly.views.status', name='status'),
    url(r'^forecast[/]?$', 'windfriendly.views.forecast', name='forecast'),
    url(r'^update/(?P<utility>[a-zA-Z0-9_-]+)[/]?$', 'windfriendly.views.update', name='update'),
    url(r'^history/(?P<userid>[a-zA-Z0-9_-]+)[/]?$', 'windfriendly.views.history', name='history'),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

if settings.DEBUG:
  urlpatterns += patterns('',
    url(r'^static/(?P<path>.*)$', 'django.views.static.serve', {
      'document_root': settings.MEDIA_ROOT,
    }),
  )
