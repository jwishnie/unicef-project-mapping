# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

from maplayers.admin_views import _add_existing_sectors, _create_and_add_new_sectors
from maplayers.admin_views import _add_existing_implementors, _create_and_add_new_implementors
from maplayers.models import Project, Sector, Implementor
from maplayers.utils import is_iter
from django.db.models import Q
from django.contrib.auth.models import Group
from maplayers.constants import PROJECT_STATUS

class AdminViewsUnitTest(TestCase):
    def setUp(self):
        self.p = Project(name="test", description="test description", latitude=0, longitude=0, created_by_id=2)
        self.p.save()
        self.p.groups.add(Group.objects.get(id=2))
        
    def teardown(self):
        self.p.delete()
    
    def test_adding_existing_sectors_to_new_project(self):
        all_sectors = Sector.objects.all()
        sector_names = ["Health", "Education"]
        _add_existing_sectors(self.p, all_sectors, sector_names)
        
        expected_sectors = Sector.objects.filter(name__in=["Health", "Education"])
        self.assertEquals(set(expected_sectors), set(self.p.sector_set.all()))
        
    def test_adding_new_sectors_to_new_project(self):
        all_sectors = Sector.objects.all()
        sector_names = ["Health", "Vaccination"]
        _create_and_add_new_sectors(self.p, all_sectors, sector_names)
        
        expected_sectors = Sector.objects.filter(name__in=["Vaccination"])
        self.assertEquals(set(expected_sectors), set(self.p.sector_set.all()))
        
    def test_adding_existing_implementors_to_new_project(self):
        all_implementors = Implementor.objects.all()
        implementor_names = ["Unicef"]
        _add_existing_implementors(self.p, all_implementors, implementor_names)
    
        expected_implementors = Implementor.objects.filter(name__in=["Unicef"])
        self.assertEquals(set(expected_implementors), set(self.p.implementor_set.all()))
    
    def test_adding_new_implementors_to_new_project(self):
        all_implementors = Implementor.objects.all()
        implementor_names = ["WHO"]
        _create_and_add_new_implementors(self.p, all_implementors, implementor_names)
    
        expected_implementors = Implementor.objects.filter(name__in=["WHO"])
        self.assertEquals(set(expected_implementors), set(self.p.implementor_set.all()))
        

class AdminViewsFunctionalTest(TestCase):
    fixtures = ['test_project_data']
    
    def test_adding_a_new_project(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='author', password='author'))
        ctxt = web_client.get("/add_project/").context
        ctxt = ( ctxt[0] if is_iter(ctxt) else ctxt )
        project_id = ctxt['project_id']
        web_client.post("/add_project/", 
                                 {"project_id": project_id,
                                  "name" : "test", "description" : "test description", 
                                  "latitude" : "-70", "longitude" : "-10", 
                                  "location" : "test location", "website_url" : "www.test.com",
                                  "project_image" : "www.image.com",
                                  "project_sectors" : "Health, TestSector",
                                  "project_implementors" : "TestImplementor, Red Cross Foundation"})

        project = Project.objects.filter(name="test")
        self.assertTrue(project)
        self.assertTrue(Sector.objects.filter(name="TestSector"))
        self.assertTrue(Implementor.objects.filter(name="TestImplementor"))
        # self.assert
        
        
    def test_editing_an_existing_project(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='author', password='author'))
        project_id = 6
        project_links = ["http://www.link1.com", "http://www.link2.com", "http://www.link3.com"]
        web_client.post("/edit_project/6/", 
                                 {"project_id": project_id,
                                  "name" : "Edited", "description" : "editied description", 
                                  "latitude" : "30", "longitude" : "45", 
                                  "location" : "edited location", "website_url" : "http://www.edited-test.com/",
                                  "project_image" : "http://www.edited-image.com/",
                                  "project_sectors" : "Education",
                                  "project_implementors" : "WHO, Red Cross Foundation",
                                  "link_title" : ["Link 1", "Link 2", "Link 3"],
                                  "link_url" : project_links})
        project = Project.objects.get(id=6)
        expected_sectors = Sector.objects.filter(name="Education")
        expected_implementors = Implementor.objects.filter(Q(name="WHO") | Q(name="Red Cross Foundation"))
        
        self.assertEquals(u"Edited", project.name)
        self.assertEquals(u"editied description", project.description)
        self.assertEquals(30, project.latitude)
        self.assertEquals(45, project.longitude)
        self.assertEquals(u"http://www.edited-test.com/", project.website_url)
        self.assertEquals(u"http://www.edited-image.com/", project.project_image)
        self.assertEquals(set(expected_sectors), set(project.sector_set.all()))
        self.assertEquals(set(expected_implementors), set(project.implementor_set.all()))
        self.assertEquals(set(project_links), set([link.url for link in project.link_set.all()]))
        
        
    def test_only_superuser_can_publish_projects(self): 
        #TODO : even trusted partners should be able to publish projects
        web_client = Client()
        response = web_client.get("/projects/id/1/")
        self.assertNotContains(response, "Unpublish")
        
        web_client.login(username='map_super', password='map_super')
        response = web_client.get("/projects/id/1/")
        self.assertContains(response, "Unpublish")
        
        response = web_client.get("/projects/id/7/")
        self.assertContains(response, "Publish")
        
    def test_publish_unpublish_should_update_project_status(self):
        web_client = Client()
        project = Project.objects.get(id=1)
        self.assertEquals(PROJECT_STATUS.PUBLISHED, project.status)
        web_client.login(username='map_super', password='map_super')
        response = web_client.get("/projects/unpublish/1/")
        project = Project.objects.get(id=1)
        self.assertEquals(PROJECT_STATUS.DRAFT, project.status)
        response = web_client.get("/projects/publish/1/")
        project = Project.objects.get(id=1)
        self.assertEquals(PROJECT_STATUS.PUBLISHED, project.status)


        
        
