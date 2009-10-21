# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import *
from maplayers import views

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    (r'^admin/(.*)', admin.site.root),
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
        {'document_root': 'static'}),
	(r'^projects/$', views.projects),
    (r'^projects/(?P<project_id>\d+)/$', views.project_details),
    (r'^projects/(?P<left>[0-9\.\-]+)/(?P<bottom>[0-9\.\-]+)/(?P<right>[0-9\.\-]+)/(?P<top>[0-9\.\-]+)', views.projects_in_map),
    (r'^projects/(?P<project_id>\d+)/$', views.project),
	(r'^$', views.homepage),
)
