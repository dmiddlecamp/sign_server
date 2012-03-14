from django.conf.urls.defaults import patterns, include, url
from django.contrib import admin
import robertsTest

# Uncomment the next two lines to enable the admin:
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^robertsTest/messages$', 'robertsTest.views.all_messages'),
#    url(r'^robertsTest/', include(robertsTest.urls.urlpatterns)),

    # Examples:
    url(r'^$', 'sign_server.views.hello_world'),
    url(r'^miniBoard/$', 'sign_server.views.mini_board'),
    # url(r'^sign_server/', include('sign_server.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)
