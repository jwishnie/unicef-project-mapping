# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from maplayers.models import Project, Video, Resource
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

    def test_get_tags_as_space_seperated(self):
        user = User.objects.create_user('author1', 'author1@email.com', 'author1') 
        project = self._create_project(user)
        project.tags = "Medical Health Vaccine"
        self.assertTrue(project.tags.__contains__("Medical"))        
        
    def test_return_true_if_project_contains_tag(self):
        user = User.objects.create_user('author1', 'author1@email.com', 'author1') 
        project = self._create_project(user)
        project.tags = "Medical Health Vaccine"
        self.assertTrue(project.contains_tag("Medical"))
        self.assertFalse(project.contains_tag("Children"))           
        
    
    def _create_project(self, user):
        admin = Group.objects.get(id=1)
        user.groups.add(admin)
        project = Project(name="Non Editable Project", description="Non editable description", latitude=30, longitude=30)
        project.created_by = user
        project.save()
        project.groups.add(admin)
        return project
        
    def test_default_video_for_project(self):
        project = self._create_project(User.objects.get(id=2))
        self.assertEquals("", project.default_video())
        video1 = Video(provider="youtube", project=project, video_id = "abcdefg", default=False, url="http://www.youtube.com/v=abcdefg")
        video2 = Video(provider="vimeo", project=project, video_id = "1234567", default=False, url="http://www.vimeo.com/1234567")
        video3 = Video(provider="vimeo", project=project, video_id = "a1b2c3", default=True, url="http://www.vimeo.com/a1b2c3")
        project.video_set.add(video1)
        project.video_set.add(video2)
        project.video_set.add(video3)
        self.assertEquals(video3, project.default_video())
        
class ResourceTest(TestCase):
    def test_is_resource_audio_file(self):
        resource = Resource()
        resource.filename = "default.aspx"
        self.assertFalse(resource.is_audio_file())

        resource.filename = "fear_of_the_dark.mp3"
        self.assertTrue(resource.is_audio_file())

        resource.filename = "bark_at_the_moon.ogg"
        self.assertTrue(resource.is_audio_file())

    def test_should_give_filesize_in_kilobytes(self):
        resource = Resource()
        resource.filesize = 1024
        self.assertEquals(resource.file_size_in_kb(), "1 KB")

    def test_should_give_file_extension_of_resource(self):
        resource = Resource()
        resource.filename = "default.current.aspx"
        self.assertEquals("aspx", resource.file_extension())

    def test_should_give_file_name_without_extension_of_resource(self):
        resource = Resource()
        resource.filename = "default.current.aspx"
        self.assertEquals("default.current", resource.file_extension())
