# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

class HomePage(TestCase):
    def test_should_get_homepage(self):
        web_client = Client()
        response = web_client.get("/", {})
        self.assertEquals(200, response.status_code)


