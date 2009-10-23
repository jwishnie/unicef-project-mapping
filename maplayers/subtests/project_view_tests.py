# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
from maplayers.models import Project

class ProjectsPage(TestCase):
    def test_should_get_list_of_projects(self):
        web_client = Client()
        response = web_client.get('/projects/', {})
        self.assertEquals(200, response.status_code)

class ProjectPage(TestCase):
    fixtures=['test_projects_data.json']
    def test_should_get_project_page(self):
        webclient = Client()
        response = webclient.get('/projects/id/1/')
        self.assertEquals(200, response.status_code)
    def test_should_return_404_if_project_doesnot_exist(self):
        webclient = Client()
        response = webclient.get('/projects/1id/000/')
        self.assertEquals(404, response.status_code)
        
    def test_should_return_list_of_projects_in_bounding_box(self):
        webclient = Client()
        context = webclient.get('/projects/bbox/0/0/40/10/').context
        self.assertEquals(40, context['right'])
        self.assertEquals(10, context['top'])
        self.assertEquals(0, context['bottom'])
        self.assertEquals(0, context['left'])
        self.assertEquals(Project.objects.get(id=1), context['projects'][0])
        
    def test_should_return_list_of_projects_in_selected_sectors(self):
        webclient = Client()
        context = webclient.post('/projects/bbox/-180/-90/180/90/', {'sector_2':'true', 'sector_3':'true'}).context
        self.assertEquals(set(Project.objects.filter(id__in=[2, 3, 4])), set(context['projects']))
    
    def test_should_return_list_of_projects_by_selected_implementors(self):
        webclient = Client()
        context = webclient.post('/projects/bbox/-180/-90/180/90/', {'implementor_1':'true'}).context
        self.assertEquals(1, len(context['projects']))
        self.assertEquals(Project.objects.get(id=1), context['projects'][0])