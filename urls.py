# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.conf.urls.defaults import patterns, include
from django.views.generic.simple import direct_to_template
from django.conf import settings

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
        (r'^accounts/login/$', 'django.contrib.auth.views.login'),
        (r'^accounts/logout/$', 'django.contrib.auth.views.logout', { 'next_page': '/' })
        )

urlpatterns += patterns('', (r'^admin/(.*)', admin.site.root))

urlpatterns += patterns('maplayers',
                        (r'^projects/bbox/(?P<left>.+)/(?P<bottom>.+)/(?P<right>.+)/(?P<top>.+)/$',
                         'views.projects_in_map'),
                         (r'^projects/id/(?P<project_id>\d+)/$', 'views.project'),
                         (r'^$', 'views.homepage'),
                         (r'^projects/search/(?P<search_term>.+)/$','views.projects_search'),
                         (r'^permission_denied/(?P<action>.+)/(?P<reason>.+)/$', direct_to_template,
                          {'template': 'permission_denied.html'}),
                         (r'^projects/tag/(?P<tag_term>.+)/$','views.projects_tag_search'),
                         )
 
urlpatterns += patterns('maplayers',
                        (r'^add_project/', 'admin_views.add_project'),
                        (r'^edit_project/(?P<project_id>\d+)/$', 'admin_views.edit_project'),
                        (r'^upload/$', 'admin_views.file_upload'),
                        (r'^remove_attachment/$', 'admin_views.remove_attachment'),
                        (r'^projects/publish/(?P<project_id>\d+)/$', 'admin_views.publish_project'),
                        (r'^projects/unpublish/(?P<project_id>\d+)/$', 'admin_views.unpublish_project'),
                        (r'^user_registration/$', 'admin_views.user_registration')
                       )

urlpatterns += patterns('',
                        (r'^tinymce/', include('tinymce.urls')))

# If in debug mode, server statics locally, otherwise the host HTTP server should do this
if settings.DEBUG:
    urlpatterns += patterns('',
                            (r'^static/(?P<path>.*)$', 
                             'django.views.static.serve',
                             {'document_root': 'static'})
                             )



