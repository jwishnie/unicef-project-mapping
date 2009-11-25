# vim: ai ts=4 sts=4 et sw=4 encoding=utf-8

from django.test import TestCase
from mock import Mock
from maplayers.templatetags import project_tags


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

    def test_should_provide_link_to_edit_only_for_authorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertTrue(project_tags.edit_project_link(project, mock_user).__contains__('/edit_project/3/'))

    def test_should_not_provide_link_to_edit_for_unauthorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertFalse(project_tags.edit_project_link(project, mock_user).__contains__('/edit_project/3/'))
        self.assertEquals(project_tags.edit_project_link(project, mock_user), '')

    def test_should_provide_add_subproject_link_only_for_authorized_user(self):
        project = Mock()
        project.is_parent_project.return_value = True
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertTrue(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_sub_project/parent_project_id/3/'))

    def test_should_not_provide_link_to_add_project_for_unauthorized_user(self):
        project = Mock()
        project.id = 3
        project.is_parent_project.return_value = True
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertFalse(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_sub_project/parent_project_id/3/'))
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
        parent_project.name = "Unicef"
        header = project_tags.sub_project_header(parent_project)
        self.assertTrue(header.__contains__('Adding Sub Project for Unicef'))

    def test_should_add_hidden_input_with_parent_id_when_adding_subproject(self):
        parent_project = Mock()
        parent_project.id = 3
        header = project_tags.sub_project_header(parent_project)
        self.assertTrue(header.__contains__('input type="hidden" name="parent_project_id" value="3"'))

    def test_should_not_add_header_when_adding_subproject(self):
        parent_project = None
        header = project_tags.sub_project_header(parent_project)
        self.assertEquals("", header)


