from django.conf.urls.default import patterns
from django.views.generic.simple import direct_to_template
from django.conf import settings


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
