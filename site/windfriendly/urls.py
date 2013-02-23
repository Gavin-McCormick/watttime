from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'windfriendly.views.home', name='home'),
    url(r'^status[/]?$', 'windfriendly.views.status', name='status'),
    url(r'^$', 'windfriendly.views.status', name='status'),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
