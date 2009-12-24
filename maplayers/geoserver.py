# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from eventlet.green import urllib2
import settings
import simplejson as json

class GeoServer(object):
    def __init__(self):
        self.url = settings.GEOSERVER_URL
    def get_list_of_countries_with_shapefiles(self):
        request_url = ""
        response = urllib2.urlopen(self.url + "/rest/workspaces.json")
        data = json.loads(response.read())
        return self.extract_countries(data)

    def extract_countries(self, data):
        workspaces = data['workspaces']['workspace']
        regions = [region['name'] for region in  workspaces]
        regions_without_world_layer = filter(lambda x: not x.__contains__('GADM'), regions)
        return regions_without_world_layer

    def get_admin_units_for_country(self, country):
        try:
            request_url = self.url + "/rest/workspaces/%s/datastores/%s/featuretypes.json" % (country, country)
            response = urllib2.urlopen(request_url)
            data = json.loads(response.read())
            return self.extract_admin_units(data)
        except urllib2.HTTPError, ex:
            return "Unable to find region data for the country"

    def extract_admin_units(self, data):
        if(isinstance(data, dict)):
            featuretypes = data['featureTypes']['featureType']
            admin_units = [admin_unit['name'] for admin_unit in featuretypes]
            return admin_units
        else:
            return data
