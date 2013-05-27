from django.conf.urls import patterns, include, url
from django.conf import settings

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

# basic patterns
urlpatterns = patterns('',
    url(r'^[/]?$', 
        'accounts.views.profile_create', name='home'),
  #  url(r'accounts', include('allauth.urls')),
    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)

# pages patterns
urlpatterns += patterns('pages.views',
    url(r'^faq[/]?$', 
        'faq', name='faq'),                
    url(r'^contact[/]?$', 
        'contact', name='contact'),                
    url(r'^about-us[/]?$', 
        'about_us', name='about-us'),                
    url(r'^how-it-works[/]?$', 
        'how_it_works', name='how-it-works'),                
)

# accounts patterns
urlpatterns += patterns('accounts.views',
   # url(r'^signup[/]?$', 
   #     'accounts.views.profile_create', name='profile_create'),
    url(r'^profile[/](?P<userid>[a-zA-Z0-9_-]+)[/]?', 
        'profile_alpha', name='profile_alpha'),
    url(r'^welcome_alpha[/]?$', 
        'welcome_alpha', name='welcome_alpha'),
    url(r'^thanks[/]?$', 
        'thanks', name='thanks'),
)

# windfriendly API patterns
urlpatterns +=  patterns('windfriendly.views',
    url(r'^status[/]?$',
        'status', name='status'),
    url(r'^forecast[/]?$',
        'forecast', name='forecast'),
    url(r'^update/(?P<utility>[a-zA-Z0-9_-]+)[/]?$',
        'update', name='update'),
    url(r'^history/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        'history', name='history'),
    url(r'^average/(?P<userid>[a-zA-Z0-9_-]+)[/]?$',
        'average_usage_for_period', name='average'),
)

# static
urlpatterns += patterns('',
                        url(r'^static/(?P<path>.*)$', 'django.views.static.serve', { 'document_root': settings.STATIC_ROOT }),
                        )
