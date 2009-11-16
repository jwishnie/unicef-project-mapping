# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client

from maplayers.utils import is_iter
from django.db.models import Q
from django.contrib.auth.models import User, Group
from maplayers.constants import PROJECT_STATUS, GROUPS

class AdminViewsFunctionalTest(TestCase):
        
    def test_create_users_should_create_project_authors_by_default(self):
        web_client = Client()
        web_client.login(username='map_super', password='map_super')
        
        response = web_client.post("/user_registration/",
                        {"username" : "user1",
                         "email" : "e@e.com",
                         "password" : "password",
                         "confirm_password" : "password"}, follow=True)
        user = User.objects.get(username="user1")
        self.assertEquals("user1", user.username)
        self.assertEquals("e@e.com", user.email)
        group = Group.objects.get(name=GROUPS.PROJECT_AUTHORS)
        self.assertEquals(1, user.groups.all().count())
        self.assertEquals(group,user.groups.all()[0])
        
    def test_confirm_password_should_match_password(self):
        web_client = Client()
        web_client.login(username='map_super', password='map_super')
   
        response = web_client.post("/user_registration/",
                        {"username" : "user2",
                         "email" : "e@e.com",
                         "password" : "password1",
                         "confirm_password" : "password",
                         "groups" : "editors_publishers, admins"}, follow=True)
        self.assertContains(response, "Passwords do not match")
        self.assertFalse(User.objects.filter(username="user2"))
        
    
    def test_change_password_for_user(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='map_super', password='map_super'))
        web_client.post("/change_password/", 
                        {"old_password" : "map_super",
                         "new_password" : "new_password",
                         "confirm_password" : "new_password"})
        web_client.logout()
        self.assertTrue(web_client.login(username='map_super', password='new_password'))
        web_client.post("/change_password/", 
                       {"old_password" : "new_password",
                        "new_password" : "map_super",
                        "confirm_password" : "map_super"})
           
           
    
