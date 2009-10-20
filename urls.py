# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import *
from maplayers.views import project_details, homepage

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^maplayers/', include('maplayers.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
	(r'^project_details', project_details),
	(r'', homepage)
)
