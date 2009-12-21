# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
from maplayers.models import Project
from maplayers.views import convert_to_json, _get_bounding_box_for_project, projects_search, GeoServer 
from maplayers.constants import PROJECT_STATUS
from  mock import Mock
from maplayers import views
from django.http import Http404
from maplayers.admin_request_parser import convert_text_to_dicts
import json

class ProjectPage(TestCase):
    fixtures = ['test_project_data']
    
    def test_should_get_project_page(self):
        webclient = Client()
        response = webclient.get('/projects/id/1/')
        self.assertEquals(200, response.status_code)

        
    def test_should_return_list_of_projects_in_bounding_box(self):
        webclient = Client()
        content = webclient.get('/projects/bbox/0/0/40/10/', {'tag' : '', 'search_term' : ''}).content
        self.assertEquals(to_json([Project.objects.get(id=1)]), content)
        
    def test_should_return_list_of_projects_in_selected_sectors(self):
        webclient = Client()
        content = webclient.get('/projects/bbox/-180/-90/180/90/', {'sector_1':'true', 'sector_2':'true', 'tag' : '', 'search_term' : ''}).content
        projects = to_json(Project.objects.filter(id__in=[1, 3, 2]))
        self.assertEquals(projects, content)
   
    def test_should_return_list_of_projects_by_selected_implementors(self):
        webclient = Client()
        content = webclient.get('/projects/bbox/-180/-90/180/90/', {'implementor_1':'true', 'tag' : '', 'search_term' : ''}).content
        projects =  Project.objects.filter(longitude__gte=-180, 
                                          longitude__lte=180,  
                                          latitude__gte=-90, 
                                          latitude__lte=90, 
                                          implementor__in=[1],
                                          status=PROJECT_STATUS.PUBLISHED
                                          )
        self.assertEquals(to_json(projects), content)


    def test_should_return_list_of_subprojects_for_selected_project(self):
        webclient = Client()
        context = webclient.get('/projects/id/1/').context
        self.assertEquals(1, len(context[0]['subprojects']))
        
    def test_should_return_list_of_projects_matching_search_term(self):
        request = Mock()
        mock_user = Mock()
        mock_admin_group = Mock()
        mock_editor_group = Mock()
        project_manager = Mock()
        filtered_projects = Mock()        
        
        mock_admin_group.name = 'admin'
        mock_editor_group.name = 'editors_publishers'
        mock_user.groups.all.return_value = [mock_admin_group, mock_editor_group]
        
        request.user = mock_user
        request.POST.get.return_value = "Congo"
        request.META = {"HTTP_REFERER" : "http://mapping"}
        project_manager.filter.return_value = filtered_projects
        filtered_projects.distinct.return_value = [MockProject(), MockProjectForSearch()]
        actual_response = projects_search(request, project_manager)
        self.assertTrue(str(actual_response).__contains__("Congo Project"))        
        self.assertTrue(str(actual_response).__contains__("Search results for"))
            
    def test_should_give_collection_of_projects_in_json(self):
        expected_result = '''[{"latitude" : 23.50, "longitude" : 45.20, "snippet" : "This is test", "id" : 3, "sectors" : ["Disaster Aid"], "implementors" : ["UNICEF"]}, {"latitude" : 23.50, "longitude" : 45.20, "snippet" : "This is test", "id" : 4, "sectors" : ["Disaster Aid"], "implementors" : ["UNICEF"]}]'''
        project1 = MockProject()
        project1.id = 3
        project1.latitude = 23.50
        project1.longitude = 45.20

        project2 = MockProject()
        project2.id = 4
        project2.latitude = 23.50
        project2.longitude = 45.20

        actual_result = convert_to_json([project1, project2])
        self.assertEquals(expected_result, actual_result)

    def test_return_404_response_if_resource_is_not_found(self):
        request = Mock()
        mock_user = Mock()
        mock_admin_group = Mock()
        mock_editor_group = Mock()
        mock_admin_group.name = 'admin'
        mock_editor_group.name = 'editors_publishers'
        mock_user.groups.all.return_value = [mock_admin_group, mock_editor_group]
        request.user = mock_user
        
        request.META = {'HTTP_REFERER' : 'http://localhost:8000'}
        response = views.view_404(request)
        self.assertEquals(404, response.status_code)


    def test_return_500_response_if_server_throws_exception(self):
        request = Mock()
        mock_user = Mock()
        mock_admin_group = Mock()
        mock_editor_group = Mock()
        mock_admin_group.name = 'admin'
        mock_editor_group.name = 'editors_publishers'
        mock_user.groups.all.return_value = [mock_admin_group, mock_editor_group]
        request.user = mock_user
        
        request.META = {'HTTP_REFERER' : 'http://localhost:8000'}
        response = views.view_500(request)
        self.assertEquals(500, response.status_code)
         
    def test_should_return_404_for_unpublished_project_request_user_not_logged_in(self):
        request = Mock()
        request.user = u'AnonymousUser'
        project_manager = Mock(Project.objects)
        project = Mock(Project)
        project.is_published.return_value = False
        project.is_editable_by.return_value = False
        project_manager.select_related(depth=1).get.return_value = project  
        self.assertRaises(Http404, views.project, request, 1, project_manager)

    def test_should_return_200_for_unpublished_project_req_user_logged_in(self):
        web_client=Client()
        self.assertTrue(web_client.login(username='author', password="author"))
        response = web_client.get("/projects/id/8")
        self.assertTrue(200, response.status_code)
        
        
    def test_bounding_box_for_project(self):
        project = MockProjectForBoundingBox({'latitude' : 1, 'longitude' : 1})
        subproject1 = MockProjectForBoundingBox({'latitude' : 1, 'longitude' : 5})
        subproject2 = MockProjectForBoundingBox({'latitude' : 1, 'longitude' : -5})
        subproject3 = MockProjectForBoundingBox({'latitude' : 5, 'longitude' : 1})
        subproject4 = MockProjectForBoundingBox({'latitude' : -5, 'longitude' : 1})
        
        bbox = _get_bounding_box_for_project(project, [subproject1, subproject2, subproject3, subproject4])
        expected_bbox = {'top': 6, 'right': 7, 'bottom': -6, 'left': -7}
        self.assertEquals(expected_bbox, bbox)

    def test_extract_country_code(self):
        self.assertEquals('IN', convert_text_to_dicts(MockGeoserver().response())["ISO2"])

    def test_get_bounding_box_of_country(self):
        request = Mock()
        request.method = 'GET'
        request.GET.get.return_value = MockGeoserver().response()
        geonames_service = Mock()
        geoserver = Mock()
        geoserver.get_admin_units_for_country.return_value = '["Districts", "County"]'
        geonames_service.query_for_country.return_value = '''
                                                          {"geonames"
                                                          :[{"countryName":"India",
                                                             "bBoxWest":68.1866760253906,
                                                             "currencyCode":"INR",
                                                             "fipsCode":"IN",
                                                             "countryCode":"IN",
                                                             "isoNumeric":"356",
                                                             "capital":"New Delhi",
                                                             "areaInSqKm":"3287590.0",
                                                             "languages":"en-IN,hi,bn,te,mr,ta,ur,gu,ml,kn,or,pa,as,ks,sd,sa,ur-IN",
                                                             "bBoxEast":97.4033126831055,
                                                             "isoAlpha3":"IND",
                                                             "continent":"AS",
                                                             "bBoxNorth":35.5042304992676,
                                                             "geonameId":1269750,
                                                             "bBoxSouth":6.74713850021362,
                                                             "population":"1147995000"}]}'''
        response = views.country_details(request, geonames_service, geoserver)
        self.assertEquals('{"north": 35.504230499267599, "west": 68.186676025390597, "admin_units": "[\\"Districts\\", \\"County\\"]", "country": "India", "east": 97.403312683105497, "adm1": "GADM:IND_adm1", "south": 6.7471385002136204}', response.content)

    def test_should_return_list_of_countries(self):
        geoserver = GeoServer()
        response = '''
                      {"workspaces":
                                    {"workspace":
                                                 [{"name":"Uganda","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/Uganda.json"},
                                                  {"name":"Afghanistan","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/Afghanistan.json"},
                                                  {"name":"GADM","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/GADM.json"}]}}'''
        self.assertEquals(["Uganda", "Afghanistan"], geoserver.extract_countries(json.loads(response)))

    def test_should_return_list_of_admin_units_for_country(self):
        geoserver = GeoServer()
        response = '''
                      {"workspaces":
                                    {"workspace":
                                                 [{"name":"Uganda","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/Uganda.json"},
                                                  {"name":"Afghanistan","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/Afghanistan.json"},
                                                  {"name":"GADM","href":"http:\/\/localhost:8080\/geoserver\/rest\/workspaces\/GADM.json"}]}}'''
        self.assertEquals(["Uganda", "Afghanistan"], geoserver.extract_countries(json.loads(response)))

def to_json(projects):
    result = []
    for project in projects:
        result.append('''{"latitude" : %.2f, "longitude" : %.2f, "snippet" : "%s", "id" : %d, "sectors" : %s, "implementors" : %s}''' %(project.latitude, project.longitude, project.snippet(), project.id, project.sectors_in_json(), project.implementors_in_json()))
    return "[" + ", ".join(result) + "]"
    
def _create_mock_project(hash_values):
    mock_project = Mock()
    for key in hash_values:
        mock_project.key = hash_values[key]
    return mock_project
    
    
class MockProject:
    def __init__(self):
        self.id = 1
        self.latitude = 30
        self.longitude = 30
    def snippet(self):
        return "This is test"
    def sectors_in_json(self):
        return '["Disaster Aid"]'
    def implementors_in_json(self):
        return '["UNICEF"]'

class MockProjectForSearch:
    def __init__(self):
        self.id = 2
        self.latitude = 30
        self.longitude = 30
    def snippet(self):
        return "Congo Project"
    def sectors_in_json(self):
        return '["Disaster Aid"]'
    def implementors_in_json(self):
        return '["UNICEF"]'
                
class MockProjectForBoundingBox(object):
    def __init__(self, init_hash):
        self.latitude = init_hash['latitude']
        self.longitude = init_hash['longitude']
        
class MockGeoserver(object):
    def response(self):
        return '''
Results for FeatureType 'gadm1_lev0':
--------------------------------------------
the_geom = [GEOMETRY (MultiPolygon) with 450007 points]
OBJECTID = 101
GADMID = 105
ISO = IND
NAME_ENGLI = India
NAME_ISO = INDIA
NAME_FAO = India
NAME_LOCAL = Bharat
NAME_OBSOL = 
NAME_VARIA = Bharat|Damão and Diu|Goa|Hindustan
NAME_NONLA = 
NAME_FRENC = Inde
NAME_SPANI = India
NAME_RUSSI = ?????
NAME_ARABI = ?????
NAME_CHINE = ??
WASPARTOF = 
CONTAINS = 
SOVEREIGN = India
ISO2 = IN
WWW = 
FIPS = IN
ISON = 356.0
VALIDFR = Unknown
VALIDTO = Present
AndyID = 113.0
POP2000 = 1.008937356E9
SQKM = 3089282.0
POPSQKM = 326.592831603
UNREGION1 = Southern Asia
UNREGION2 = Asia
DEVELOPING = 1.0
CIS = 0.0
Transition = 0.0
OECD = 0.0
WBREGION = South Asia
WBINCOME = Low income
WBDEBT = Less indebted
WBOTHER = 
CEEAC = 0.0
CEMAC = 0.0
CEPLG = 0.0
COMESA = 0.0
EAC = 0.0
ECOWAS = 0.0
IGAD = 0.0
IOC = 0.0
MRU = 0.0
SACU = 0.0
UEMOA = 0.0
UMA = 0.0
PALOP = 0.0
PARTA = 0.0
CACM = 0.0
EurAsEC = 0.0
Agadir = 0.0
SAARC = 1.0
ASEAN = 0.0
NAFTA = 0.0
GCC = 0.0
CSN = 0.0
CARICOM = 0.0
EU = 0.0
CAN = 0.0
ACP = 0.0
Landlocked = 0.0
AOSIS = 0.0
SIDS = 0.0
Islands = 0.0
LDC = 0.0
Shape_Leng = 335.902226422
Shape_Area = 278.699431993
--------------------------------------------
        '''
