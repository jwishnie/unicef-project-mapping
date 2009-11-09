# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

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
        
    def test_should_get_projects_from_bookmarked_url(self):
        context = self.web_client.get("/", {"left" : "-60", "bottom" : "-30", 
                                       "right" : "60", "top" : "10", 
                                       "sector_1" : "true",
                                       "implementor_1" : "true"}).context
                                       

