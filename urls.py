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
                        (r'^user_registration/$', 'views.user_registration'),
                        (r'^change_password/$', 'views.change_password'),
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
                         (r'^projects/(?P<project_id>\d+)/comment/$','views.project_comment'),
                         (r'^search_admin_unit/$', 'views.search_admin_units'),
                         )
                         
urlpatterns += patterns('maplayers.project_admin_views',
                        (r'^add_project', 'add_project'),
                        (r'^edit_project/(?P<project_id>\d+)/$', 'edit_project'),
                        (r'^projects/upload/$', 'file_upload'),
                        (r'^remove_attachment/$', 'remove_attachment'),
                        (r'^projects/publish/(?P<project_id>\d+)/$', 'publish_project'),
                        (r'^projects/unpublish/(?P<project_id>\d+)/$', 'unpublish_project'),
                        (r'^projects/reject/(?P<project_id>\d+)/$', 'reject_project'),
                        (r'^projects/delete/(?P<project_id>\d+)/$', 'delete_project'),
                        (r'^request_changes/(?P<project_id>\d+)/$', 'request_changes'),
                        (r'^projects/comments/(?P<project_id>\d+)/$', 'project_comments'),
                        (r'^projects/comments/publish/$', 'publish_comments'),
                        (r'^projects/comments/delete/$', 'delete_comments'),
                       )
 
urlpatterns += patterns('maplayers.admin_views',
                        (r'^my_projects/$', 'my_projects'),
                        (r'^projects_for_review/$', 'projects_for_review'),
                        (r'^projects/review_suggestions/(?P<project_id>\d+)/$', 'review_suggestions'),
                        (r'^admin_units/', 'admin_units'),
                        (r'^add_admin_unit/', 'add_administrative_unit'),
                        (r'^edit_admin_unit/(?P<id>\d+)/$', 'edit_administrative_unit'),
                        (r'^delete_admin_unit/(?P<id>\d+)/$', 'delete_administrative_unit'),
                        (r'^add_kml/$', 'add_kml_file'),
                        (r'^delete_kml/(?P<id>\d+)/$', 'delete_kml'),
                       )

urlpatterns += patterns('',
                        (r'^tinymce/', include('tinymce.urls')))
                        

handler404 = 'maplayers.views.view_404'
handler500 = 'maplayers.views.view_500'

urlpatterns += patterns('',
                        (r'^static/(?P<path>.*)$', 
                         'django.views.static.serve',
                         {'document_root': 'static'})
                         )



