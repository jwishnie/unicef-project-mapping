# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from eventlet.green import urllib2
import settings
import simplejson as json

class GeoNames(object):
    def __init__(self):
        self.url = settings.GEONAMES_URL
    def query_for_country(self,country_code):
        try:
            request_url = self.url + str(country_code)
            data = urllib2.urlopen(str(request_url)).read()
            return data
        except urllib2.HTTPError, ex:
            
            return ""

