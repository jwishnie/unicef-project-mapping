# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from maplayers.models import Project

class ProjectPage(TestCase):
    fixtures = ['test_project_data']
    
    def test_should_get_list_of_project_implementors_in_json(self):
        project = Project.objects.get(id=3)
        self.assertEquals('["Red Cross Foundation", "Doctors Without Borders"]', project.implementors_in_json())
        
    def test_should_get_list_of_project_sectors_in_json(self):
        project = Project.objects.get(id=3)
        self.assertEquals('["Health", "Disaster Aid"]', project.sectors_in_json())    