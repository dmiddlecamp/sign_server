from django.conf.urls.defaults import patterns, url
from django.contrib import admin
import robertsTest.views

admin.autodiscover()

urlpatterns = patterns(''
#    url(r'/robertsTest/messages', robertsTest.views.all_messages),
)
