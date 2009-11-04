# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

from maplayers.admin_views import _add_existing_sectors, _create_and_add_new_sectors
from maplayers.admin_views import _add_existing_implementors, _create_and_add_new_implementors
from maplayers.models import Project, Sector, Implementor
from maplayers.utils import is_iter
from django.db.models import Q

class AdminViewsUnitTest(TestCase):
    def setUp(self):
        self.p = Project(name="test", description="test description", latitude=0, longitude=0)
        self.p.save()
        
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
                                  "project_sectors" : "Health, Education",
                                  "project_implementors" : "TestImplementor, Red Cross Foundation"})

        self.assertTrue(Project.objects.filter(name="test"))
        self.assertTrue(Sector.objects.filter(name="TestSector"))
        self.assertTrue(Implementor.objects.filter(name="TestImplementor"))
        
        
    def test_editing_an_existing_project(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='author', password='author'))
        project_id = 6
        project_links = ["http://www.link1.com", "http://www.link2.com", "http://www.link3.com"]
        web_client.post("/edit_project/6", 
                                 {"project_id": project_id,
                                  "name" : "Edited", "description" : "editied description", 
                                  "latitude" : "30", "longitude" : "45", 
                                  "location" : "edited location", "website_url" : "www.edited-test.com",
                                  "project_image" : "www.edited-image.com",
                                  "project_sectors" : "Education",
                                  "project_implementors" : "WHO, Red Cross Foundation",
                                  "link_title" : ["Link 1", "Link 2", "Link 3"],
                                  "link_url" : project_links})
        project = Project.objects.get(id=6)
        expected_sectors = Sector.objects.filter(name="Education")
        expected_implementors = Implementor.objects.filter(Q(name="WHO") | Q(name="Red Cross Foundation"))
        
        self.assertTrue("Edited", project.name)
        self.assertTrue("editied description", project.description)
        self.assertTrue(30, project.latitude)
        self.assertTrue(45, project.longitude)
        self.assertTrue("www.edited-test.com", project.website_url)
        self.assertTrue("www.edited-image.com", project.project_image)
        self.assertTrue(expected_sectors, project.sector_set.all())
        self.assertTrue(expected_implementors, project.implementor_set.all())
        self.assertTrue(set(project_links), set([link.url for link in project.link_set.all()]))
        