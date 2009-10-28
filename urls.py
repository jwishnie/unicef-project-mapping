# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns
from django.views.generic.simple import direct_to_template
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

pats = [
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout', { 'next_page': '/' }),
        (r'^admin/(.*)', admin.site.root),
        (r'^projects/bbox/(?P<left>.+)/(?P<bottom>.+)/(?P<right>.+)/(?P<top>.+)/$', 
            'maplayers.views.projects_in_map'),
        (r'^projects/id/(?P<project_id>\d+)/$', 'maplayers.views.project'),
        (r'^$', 'maplayers.views.homepage'),
        (r'^add_project/', 'maplayers.admin_view.add_project'),
        (r'^project_created_successfully/', direct_to_template, {'template': 'project_created_successfully.html'})
    ]

# If in debug mode, server statics locally, otherwise the host HTTP server should do this
if settings.DEBUG:
    static_serve = (r'^static/(?P<path>.*)$', 'django.views.static.serve',
                    {'document_root': 'static'})
    pats.insert(0,static_serve)

urlpatterns = patterns('', *pats)

