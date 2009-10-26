# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

class HomePage(TestCase):
    def test_should_get_homepage(self):
        web_client = Client()
        response = web_client.get("/", {})
        self.assertEquals(200, response.status_code)
        
    def test_should_get_projects_from_bookmarked_url(self):
        web_client = Client()
        context = web_client.get("/", {"left" : "-60", "bottom" : "-30", 
                                       "right" : "60", "top" : "10", 
                                       "sector_1" : "true",
                                       "implementor_1" : "true"}).context
                                       

