# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
from maplayers.models import Project
from maplayers.views import convert_to_json, _get_bounding_box_for_project, projects_search
from maplayers.constants import PROJECT_STATUS
from  mock import Mock
from maplayers import views
from django.http import Http404

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
        
        
