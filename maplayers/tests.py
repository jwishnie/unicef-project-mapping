# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client


class HomePage(TestCase):
    def test_should_get_homepage(self):
        web_client = Client()
        response = web_client.get("/", {})
        self.assertEquals(200, response.status_code)

class ProjectsPage(TestCase):
    def test_should_get_list_of_projects(self):
        web_client = Client()
        response = web_client.get('/projects/', {})
        self.assertEquals(200, response.status_code)


class ProjectPage(TestCase):
    fixtures=['test_projects_data.json']
    def test_should_get_project_page(self):
        webclient = Client()
        response = webclient.get('/projects/1/')
        self.assertEquals(200, response.status_code)
    def test_should_return_404_if_project_doesnot_exist(self):
        webclient = Client()
        response = webclient.get('/projects/1000/')
        self.assertEquals(404, response.status_code)
