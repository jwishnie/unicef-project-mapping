# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
from maplayers.models import Project

class ProjectPage(TestCase):
    fixtures = ['test_project_data']
    
    def test_should_get_project_page(self):
        webclient = Client()
        response = webclient.get('/projects/id/1/')
        self.assertEquals(200, response.status_code)

        
    def test_should_return_list_of_projects_in_bounding_box(self):
        webclient = Client()
        context = webclient.get('/projects/bbox/0/0/40/10/', {'tag' : ''}).context
        self.assertEquals(Project.objects.get(id=1), context['projects'][0])
        
    def test_should_return_list_of_projects_in_selected_sectors(self):
        webclient = Client()
        context = webclient.get('/projects/bbox/-180/-90/180/90/', {'sector_1':'true', 'sector_2':'true', 'tag' : ''}).context
        projects = Project.objects.filter(id__in=[1, 3, 2])
        self.assertEquals(set(projects), set(context['projects']))
   
    def test_should_return_list_of_projects_by_selected_implementors(self):
        webclient = Client()
        context = webclient.get('/projects/bbox/-180/-90/180/90/', {'implementor_1':'true', 'tag' : ''}).context
        projects =  Project.objects.filter(longitude__gte=-180, 
                                          longitude__lte=180,  
                                          latitude__gte=-90, 
                                          latitude__lte=90, 
                                          implementor__in=[1]
                                          )
        self.assertEquals(set(projects), set(context['projects']))


    def test_should_return_list_of_subprojects_for_selected_project(self):
        webclient = Client()
        context = webclient.get('/projects/id/1/').context
        self.assertEquals(1, len(context[0]['subprojects']))
        
    def test_should_return_list_of_projects_in_json_matching_search_term(self):
        webclient = Client()
        response = webclient.get('/projects/search/unicef/')
        self.assertContains(response, "School for all")
        self.assertContains(response, "'implementors' : [\"Unicef\"]")

