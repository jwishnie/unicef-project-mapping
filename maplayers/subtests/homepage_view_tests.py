# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
from maplayers.views import search_admin_units
from mock import Mock

class HomePage(TestCase):
    def setUp(self):
        self.web_client = Client()
        
    def test_should_get_homepage(self):
        response = self.web_client.get("/", {})
        self.assertEquals(200, response.status_code)
        
    def test_should_not_contain_add_project_link_if_not_authenticated(self):
        response = self.web_client.get("/", {})
        self.assertNotContains(response, "Add a new project")
        
    def test_should_contain_add_project_link_if_authenticated(self):
        self.assertTrue(self.web_client.login(username='author', password='author'))
        response = self.web_client.get("/", {})
        self.assertContains(response, "Add a new project")
        
    def test_should_not_contain_my_projects_link_if_not_authenticated(self):
        response = self.web_client.get("/", {})
        self.assertNotContains(response, "My Projects")
    
    def test_should_contain_my_projects_link_if_authenticated(self):
        self.assertTrue(self.web_client.login(username='author', password='author'))
        response = self.web_client.get("/", {})
        self.assertContains(response, "My Projects")        
        
    def test_should_get_projects_from_bookmarked_url(self):
        context = self.web_client.get("/", {"left" : "-60", "bottom" : "-30", 
                                       "right" : "60", "top" : "10", 
                                       "sector_1" : "true",
                                       "implementor_1" : "true"}).context
                                       
    def test_should_get_custom_404_page_on_page_not_found(self):
        response = self.web_client.get("/blah", {})
        self.assertContains(response, "Something's gone a bit wrong!", status_code=404)
        
    def test_admin_units(self):
        geoServer = MockGeoServer()
        request = Mock()
        request.method = 'GET'
        request.GET.get.return_value = geoServer.get_feature_info()
        httpResponse = search_admin_units(request)
        self.assertTrue('{"infrastructure": "", "name": "Gulu", "country": "Uganda", "governance": "", "dev_partners": "", "environment": "", "recent_reports": "", "health": "", "social_sector": "", "region_type": "District", "found": true, "agriculture": "", "id": 1, "resources": "", "economy": ""}', httpResponse.content)



class MockGeoServer:
    def get_feature_info(self):
        return '''
        Results for FeatureType 'UGA_adm1':
        --------------------------------------------
        the_geom = [GEOMETRY (MultiPolygon) with 5343 points]
        ID_0 = 230
        ISO = UGA
        NAME_0 = Uganda
        ID_1 = 3085
        NAME_1 = Gulu
        VARNAME_1 = 
        NL_NAME_1 = 
        HASC_1 = UG.GL
        CC_1 = 30
        TYPE_1 = District
        ENGTYPE_1 = District
        VALIDFR_1 = ~1991
        VALIDTO_1 = Present
        REMARKS_1 = 
        Shape_Leng = 6.18556239589
        Shape_Area = 0.964003622127
        --------------------------------------------
                '''

        
        
