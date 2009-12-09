# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from django.test.client import Client
import re

from maplayers.project_admin_views import _add_existing_sectors, _create_and_add_new_sectors
from maplayers.project_admin_views import _add_existing_implementors, _create_and_add_new_implementors
from maplayers.models import Project, Sector, Implementor, ProjectComment
from maplayers.utils import is_iter
from django.db.models import Q
from django.contrib.auth.models import User, Group
from maplayers.constants import PROJECT_STATUS, VIMEO_REGEX, YOUTUBE_REGEX
from mock import Mock
from maplayers import project_admin_views as views

class ProjectAdminViewsUnitTest(TestCase):
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
        
        fixtures = ['test_project_data']

    def test_adding_a_new_project(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='author', password='author'))
        ctxt = web_client.get("/add_project?parent_id=").context
        ctxt = ( ctxt[0] if is_iter(ctxt) else ctxt )
        project_id = ctxt['project'].id
        web_client.post("/add_project?parent_id=", 
                                 {"project_id": project_id,
                                  "name" : "test_add", "description" : "test description", 
                                  "latitude" : "-70", "longitude" : "-10", 
                                  "location" : "test location", "website_url" : "www.test.com",
                                  "project_image" : "www.image.com",
                                  "project_sectors" : "Health, TestSector",
                                  "project_implementors" : "TestImplementor, Red Cross Foundation",
                                  "tags": "Health Medical"})

        project = Project.objects.get(name__exact="test_add")
        self.assertTrue(project)
        self.assertTrue(PROJECT_STATUS.DRAFT, project.status)
        self.assertTrue(Sector.objects.filter(name="TestSector"))
        self.assertTrue(Implementor.objects.filter(name="TestImplementor"))


    def test_editing_an_existing_project(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='editor', password='editor'))
        project_id = 6
        project_links = ["http://www.link1.com", "http://www.link2.com", "http://www.link3.com"]
        web_client.post("/edit_project/6/", 
                                 {"project_id": project_id,
                                  "name" : "Edited", "description" : "editied description", 
                                  "latitude" : "30", "longitude" : "45", 
                                  "location" : "edited location", "website_url" : "http://www.edited-test.com/",
                                  "project_sectors" : "Education",
                                  "project_implementors" : "WHO, Red Cross Foundation",
                                  "link_title" : ["Link 1", "Link 2", "Link 3"],
                                  "publish_project" : "on",
                                  "link_url" : project_links})
        project = Project.objects.get(id=6)
        expected_sectors = Sector.objects.filter(name="Education")
        expected_implementors = Implementor.objects.filter(Q(name="WHO") | Q(name="Red Cross Foundation"))

        self.assertEquals(u"Edited", project.name)
        self.assertTrue(project.is_published())
        self.assertEquals(u"editied description", project.description)
        self.assertEquals(30, project.latitude)
        self.assertEquals(45, project.longitude)
        self.assertEquals(u"http://www.edited-test.com/", project.website_url)
        self.assertEquals(set(expected_sectors), set(project.sector_set.all()))
        self.assertEquals(set(expected_implementors), set(project.implementor_set.all()))
        self.assertEquals(set(project_links), set([link.url for link in project.link_set.all()]))


    def test_user_can_edit_project_only_if_editor_publisher_or_creator(self):
        web_client = Client()
        self.assertTrue(web_client.login(username='author', password='author'))
        response = web_client.get("/projects/id/3/")
        self.assertNotContains(response, "Edit this project")
        web_client.logout()
        self.assertTrue(web_client.login(username='editor', password='editor'))
        response = web_client.get("/projects/id/3/")
        self.assertContains(response, "Edit this project")

    def test_only_editors_can_publish_projects(self): 
        web_client = Client()
        response = web_client.get("/projects/id/1/")
        self.assertNotContains(response, "Unpublish")

        web_client.login(username='editor', password='editor')
        response = web_client.get("/projects/id/1/")
        self.assertContains(response, "Unpublish")
        
    def test_publish_unpublish_should_update_project_status(self):
        web_client = Client()
        project = Project.objects.get(id=1)
        self.assertTrue(project.is_published())
        web_client.login(username='map_super', password='map_super')
        response = web_client.get("/projects/unpublish/1/")
        project = Project.objects.get(id=1)
        self.assertEquals(PROJECT_STATUS.UNPUBLISHED, project.status)

    def test_reject_project_should_place_the_project_in_rejected_state(self):
        web_client = Client()
        project = Project.objects.get(id=1)
        self.assertTrue(project.is_published())
        web_client.login(username='map_super', password='map_super')
        response = web_client.get("/projects/reject/1/")
        project = Project.objects.get(id=1)
        self.assertEquals(PROJECT_STATUS.REJECTED, project.status)
        
    def test_delete_project(self):
        web_client = Client()
        project = Project.objects.get(id=1)
        project_name = project.name
        web_client.login(username='map_super', password='map_super')
        response = web_client.get("/projects/delete/1/")
        self.assertFalse(Project.objects.filter(name__exact=project_name))
        
    def test_publish_project_comment(self):
        web_client = Client()
        web_client.login(username='author', password='author')
        response = web_client.post("/projects/comments/publish/", {"comment_1" : True, "project_id" : "2"})
        comment = ProjectComment.objects.get(id=1)
        self.assertEquals("Published", comment.status)
        
    def test_delete_project_comment(self):
        web_client = Client()
        web_client.login(username='author', password='author')
        web_client.post("/projects/comments/delete/", {"comment_2" : True, "project_id" : "2"})
        comment = ProjectComment.objects.filter(id=2)
        self.assertFalse(comment)

    def test_allow_only_authors_to_add_project(self):
        group = Mock()
        group.name = "User"
        user = Mock()
        user.groups.all.return_value = [group]
        meta = {'QUERY_STRING' : 'parent_id=1'}
        request = Mock()
        request.user = user 
        request.META = meta
        response = views.add_project(request)
        self.assertEquals(302, response.status_code)
        self.assertEquals('/permission_denied/add_project/not_author', response.items()[1][1])

    def test_return_project_form_with_project_id(self):
        pass

    def test_youtube_regex(self):
        youtube_url = "http://www.youtube.com/watch?v=ezkxxpwPvic"
        pattern = re.compile(YOUTUBE_REGEX)
        video_id = pattern.match(youtube_url).group(1)
        self.assertEquals("ezkxxpwPvic", video_id)

    def test_vimeo_regex(self):
        vimeo_url = "http://vimeo.com/7715536"
        pattern = re.compile(VIMEO_REGEX)
        video_id = pattern.match(vimeo_url).group(1)
        self.assertEquals("7715536", video_id)


