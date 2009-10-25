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
    (r'^projects/bbox/(?P<left>.+)/(?P<bottom>.+)/(?P<right>.+)/(?P<top>.+)/$', views.projects_in_map),
    (r'^projects/id/(?P<project_id>\d+)/$', views.project),
    (r'^gallery/(?P<gallery_type>\w+)?', views.gallery),
	(r'^$', views.homepage),
)
