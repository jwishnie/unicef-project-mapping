# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from mock import Mock
from maplayers.templatetags import project_tags
from maplayers.models import Project
from django.contrib.auth.models import User, Group

class ProjectTagsTest(TestCase):
    def test_should_display_flash_message(self):
        request = Mock()
        request.session = {'message' : 'project created'}
        actual = project_tags.flash_message(request)
        expected = '<div class="flash_message_box"><div class="flash_message">project created</div></div>'
        self.assertEquals(expected, actual)

    def test_should_delete_flash_message_from_session_after_display(self):
        request = Mock()
        request.session = {'message' : 'project created'}
        project_tags.flash_message(request)
        self.assertEquals({}, request.session)

    def test_should_give_empty_message_if_no_message_is_in_session(self):
        request = Mock()
        request.session = {}
        actual = project_tags.flash_message(request)
        self.assertEquals("", actual)

    def test_should_allow_authorized_users_to_edit_project(self):
        project = Mock()
        project.is_parent_project.return_value = True
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertTrue(project_tags.edit_project_link(project, mock_user).__contains__('/edit_project/3/'))

    def test_should_not_allow_unauthorized_users_to_edit_project(self):
        project = Mock()
        project.is_parent_project.return_value = True
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertFalse(project_tags.edit_project_link(project, mock_user).__contains__('/edit_project/3/'))
        self.assertEquals(project_tags.edit_project_link(project, mock_user), '')

    def test_should_allow_authorized_users_to_add_admin_unit(self):
        request = Mock()
        mock_user = Mock()
        mock_user.is_superuser = True
                
        mock_admin_group = Mock()
        mock_editor_group = Mock()
        mock_admin_group.name = 'admin'
        mock_editor_group.name = 'editors_publishers'
        mock_user.groups.all.return_value = [mock_admin_group, mock_editor_group]
        
        request.user = mock_user        
        self.assertTrue(project_tags.add_admin_unit_related_links(mock_user).__contains__('/add_admin_unit'))

    def test_should_not_allow_unauthorized_users_to_add_admin_units(self):
        request = Mock()
        mock_user = Mock()
        mock_user.is_superuser = False
                
        mock_user.groups.all.return_value = []
        
        request.user = mock_user
        self.assertFalse(project_tags.add_admin_unit_related_links(mock_user).__contains__('/add_admin_unit'))
        self.assertEquals(project_tags.add_admin_unit_related_links(mock_user), '')

    def test_should_allow_authorized_user_to_add_project(self):
        project = Mock()
        project.is_parent_project.return_value = True
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertTrue(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_project?parent_id='))

    def test_should_not_allow_unauthorized_users_to_add_project(self):
        project = Mock()
        project.id = 3
        project.is_parent_project.return_value = True
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertFalse(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_project?parent_id=3'))
        self.assertEquals(project_tags.add_sub_project_link(project, mock_user), '')

    def test_should_not_provide_add_sub_projects_link_for_sub_projects(self):
        project = Mock()
        project.is_parent_project.return_value = False
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertEquals(project_tags.add_sub_project_link(project, mock_user), '')

    def test_should_add_header_when_adding_subproject(self):
        parent_project = Mock()
        parent_project.name = "UNICEF"
        header = project_tags.sub_project_header(parent_project)
        self.assertTrue(header.__contains__('UNICEF'))

    def test_should_add_hidden_input_with_parent_id_when_adding_subproject(self):
        parent_project = Mock()
        parent_project.id = 3
        header = project_tags.sub_project_header(parent_project)
        self.assertTrue(header.__contains__('input type="hidden" name="parent_project_id" value="3"'))

    def test_should_not_add_header_when_adding_subproject(self):
        parent_project = None
        header = project_tags.sub_project_header(parent_project)
        self.assertEquals("", header)

    def test_should_change_flickr_image_from_feed_to_thumbnail(self):
        image_url = "http://www.flickr.com/static/unicef_m.jpg"
        self.assertEquals('http://www.flickr.com/static/unicef_s.jpg', project_tags.get_thumbnail_img(image_url))
        
    def test_should_change_flickr_image_from_medium_to_actual(self):
        image_url = "http://www.flickr.com/static/unicef_m.jpg"
        self.assertEquals('http://www.flickr.com/static/unicef.jpg', project_tags.get_img(image_url))
        
    def test_should_return_excel_resource_icon_link_based_on_file_extension(self):
        resource = Mock()
        resource.title = "excel-resource.xls"
        self.assertEquals('/static/img/ms_excel.jpg', project_tags.resource_icon(resource))

    def test_should_return_word_resource_icon_link_based_on_file_extension(self):
        resource = Mock()
        resource.title = "excel-resource.doc"
        self.assertEquals('/static/img/ms_word.jpg', project_tags.resource_icon(resource))

    def test_should_return_mp3_resource_icon_link_based_on_file_extension(self):
        resource = Mock()
        resource.title = "excel-resource.mp3"
        self.assertEquals('/static/img/mp3.jpg', project_tags.resource_icon(resource))                    

    def test_should_return_no_resource_icon_link_if_extension_not_supported(self):
        resource = Mock()
        resource.title = "excel-resource.xyz"
        self.assertEquals('', project_tags.resource_icon(resource))        
        
    ### Non Mock tests    
    def test_my_projects_link_should_show_notifications(self):
        author = User.objects.get(id=2)
        html_snippet = project_tags.my_projects_link(author)
        self.assertEquals('<a href="/my_projects/" id="my_projects_link">My Projects<span class="notification">3</span></a>', html_snippet)
        
        map_super = User.objects.get(id=1)
        html_snippet = project_tags.my_projects_link(map_super)
        self.assertEquals('<a href="/my_projects/" id="my_projects_link">My Projects</a>', html_snippet)
        

    def test_projects_for_Review_link_should_show_notifications(self):
        editor = User.objects.get(id=5)
        html_snippet = project_tags.projects_for_review_link(editor)
        self.assertEquals('<li id="projs_for_review_li"><a href="/projects_for_review/">Projects for Review<span class="notification">3</span></a></li>', html_snippet)

    def test_should_no_resource_list_if_no_resources_are_available(self):
        resources = []
        html = project_tags.resource_list(resources)
        self.assertEquals("", html)

