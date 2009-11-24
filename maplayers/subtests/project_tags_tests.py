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

    def test_should_give_empty_string_for_link_for_unauthorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertEquals(project_tags.edit_project_link(project, mock_user), '')

    def test_should_provide_add_subproject_link_only_for_authorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = True
        self.assertTrue(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_sub_project/parent_id/3/'))

    def test_should_not_provide_link_to_edit_for_unauthorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertFalse(project_tags.add_sub_project_link(project, mock_user).__contains__('/add_sub_project/parent_id/3/'))

    def test_should_give_empty_string_for_link_for_unauthorized_user(self):
        project = Mock()
        project.id = 3
        mock_user = object()
        project.is_editable_by.return_value = False
        self.assertEquals(project_tags.add_sub_project_link(project, mock_user), '')
