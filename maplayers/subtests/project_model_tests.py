# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from maplayers.models import Project
from django.contrib.auth.models import User, Group

class ProjectModelTest(TestCase):
    
    def test_should_get_list_of_project_implementors_in_json(self):
        project = Project.objects.get(id=3)
        self.assertEquals('["Red Cross Foundation", "Doctors Without Borders"]', project.implementors_in_json())
        
    def test_should_get_list_of_project_sectors_in_json(self):
        project = Project.objects.get(id=3)
        self.assertEquals('["Health", "Disaster Aid"]', project.sectors_in_json())    
        
    def test_only_creators_and_group_members_can_edit_the_project(self):
        user = User.objects.create_user('author1', 'author1@email.com', 'author1') 
        project = self._create_project(user)
        non_editing_user = User.objects.get(id=2)
        self.assertFalse(project.is_editable_by(non_editing_user))
        self.assertTrue(project.is_editable_by(user))
        
    
    def _create_project(self, user):
        admin = Group.objects.get(id=1)
        user.groups.add(admin)
        project = Project(name="Non Editable Project", description="Non editable description", latitude=30, longitude=30, tags="Medical Health Children")
        project.created_by = user
        project.save()
        project.groups.add(admin)
        return project
