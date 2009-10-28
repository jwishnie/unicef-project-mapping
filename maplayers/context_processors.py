# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

'''
Context processor to add key settings from settings.py to RequestContext


Created on Oct 28, 2009

@author: Jeff wishnie
'''

from django.conf import settings

def add_settings(request):
    return {'static_url': settings.STATIC_URL,
            'css_url': '%s%s' % (settings.STATIC_URL, '/css'),
            'js_url': '%s%s' % (settings.STATIC_URL, '/js'),
            'img_url': '%s%s' % (settings.STATIC_URL, '/img'),
            'jquery': settings.JQUERY,
            'jquery_plugins_url': settings.JQUERY_PLUGINS,
            'openlayers': settings.OPENLAYERS,
            'mootools': settings.MOOTOOLS
            }
