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
                         (r'^user_registration/success/$', direct_to_template, 
                          {'template' : 'registration_success.html', 'message' : 'User Created'}),
                         (r'^change_password/success/$', direct_to_template, 
                          {'template' : 'registration_success.html', 'message' : 'Password changed'}),
                         (r'^projects/tag/(?P<tag_term>.+)/$','views.projects_tag_search'),
                         )
                         
urlpatterns += patterns('maplayers.project_admin_views',
                        (r'^add_project/', 'add_project'),
                        (r'^add_admin_unit/', 'add_administrative_unit'),
                        (r'^edit_project/(?P<project_id>\d+)/$', 'edit_project'),
                        (r'^upload/$', 'file_upload'),
                        (r'^remove_attachment/$', 'remove_attachment'),
                        (r'^projects/publish/(?P<project_id>\d+)/$', 'publish_project'),
                        (r'^projects/unpublish/(?P<project_id>\d+)/$', 'unpublish_project'),
                        (r'^projects/reject/(?P<project_id>\d+)/$', 'reject_project'),
                        (r'^projects/delete/(?P<project_id>\d+)/$', 'delete_project'),
                        (r'^request_changes/(?P<project_id>\d+)/$', 'request_changes'),
                       )
 
urlpatterns += patterns('maplayers.admin_views',
                        (r'^user_registration/$', 'user_registration'),
                        (r'^change_password/$', 'change_password'),
                        (r'^my_projects/$', 'my_projects'),
                        (r'^projects_for_review/$', 'projects_for_review'),
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



