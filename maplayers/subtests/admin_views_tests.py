# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

from maplayers.admin_views import _add_existing_sectors, _create_and_add_new_sectors
from maplayers.admin_views import _add_existing_implementors, _create_and_add_new_implementors
from maplayers.models import Project, Sector, Implementor
from maplayers.utils import is_iter

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
        id = ctxt['project_id']
        web_client.post("/add_project/", 
                                 {"project_id": id,
                                  "name" : "test", "description" : "test description", 
                                  "latitude" : "-70", "longitude" : "-10", 
                                  "location" : "test location", "website_url" : "www.test.com",
                                  "project_image" : "www.image.com",
                                  "project_sectors" : "Health, TestSector",
                                  "project_implementors" : "TestImplementor, Red Cross Foundation"})
        
        
        
        self.assertTrue(Project.objects.filter(name="test"))
        self.assertTrue(Sector.objects.filter(name="TestSector"))
        self.assertTrue(Implementor.objects.filter(name="TestImplementor"))
 
 
        
        
        