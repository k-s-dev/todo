from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework.exceptions import status
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.request import Request
from rest_framework.parsers import JSONParser

from core import models as core_models
from api import serializers as api_serializers


class CustomTestCaseSetup(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.api_factory = APIRequestFactory()
        temp_get_request = cls.api_factory.get(
            '/', content_type='application/json')
        cls.request_tmp = Request(temp_get_request, parsers=[JSONParser()])

    @classmethod
    def create_user(cls, username='user-1', password='testpass123'):
        """Create and return user."""
        return get_user_model().objects.create_user(username=username, password=password)


class WorkspaceCommentApiMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = cls.create_user()
        cls.view_name_list = "api:workspace-comment-list"
        cls.view_name_detail = "api:workspace-comment-detail"

    def setUp(self):
        super().setUp()
        self.client = APIClient(enforce_csrf_checks=True)
        self.client.force_authenticate(self.user)

    @staticmethod
    def get_workspace_query(pk_seq=None):
        if pk_seq:
            return core_models.Workspace.objects.filter(pk__in=pk_seq)
        return core_models.Workspace.objects.all()

    @staticmethod
    def get_comment_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.WorkspaceComment.objects.all()
        if pk_seq:
            qry = qry.filter(pk__in=pk_seq)
        if ws_pk_seq:
            qry = qry.filter(workspace__pk__in=ws_pk_seq)
        return qry

    @classmethod
    def db_create_workspaces(cls, user, multiple=True):
        cls.workspace_1 = core_models.Workspace.objects.create(
            name="default",
            created_by=user,
            is_default=True,
        )
        if multiple:
            cls.workspace_2 = core_models.Workspace.objects.create(
                name="ws 2",
                created_by=user,
                is_default=False,
            )

    @classmethod
    def db_create_comments(cls, user, workspace, multiple=True):
        comment_1_attr_name = f'ws_{workspace.pk}_comment_1'
        setattr(cls, comment_1_attr_name,
                core_models.WorkspaceComment.objects.create(
                    content="comment 1",
                    workspace=workspace,
                    created_by=cls.user,
                ))
        if multiple:
            comment_2_attr_name = f'ws_{workspace.pk}_comment_2'
            setattr(cls, comment_2_attr_name,
                    core_models.WorkspaceComment.objects.create(
                        content="comment 2",
                        workspace=workspace,
                        created_by=cls.user,
                    ))

    @classmethod
    def get_comment_serializers(cls, pk_seq=None, ws_pk_seq=None):
        comment_query = cls.get_comment_query(
            pk_seq=pk_seq, ws_pk_seq=ws_pk_seq).order_by("id")
        return api_serializers.WorkspaceCommentSerializer(
            comment_query, many=True, context={"request": cls.request_tmp},
        )


class WorkspaceCommentApiFullSetupTestClass(WorkspaceCommentApiMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_comments(cls.user, workspace)

    def setUp(self):
        super().setUp()


class WorkspaceCommentApiAuthAndCrudTests(WorkspaceCommentApiFullSetupTestClass):
    """Test basic auth and CRUD operations on comment view api."""

    def test_auth_required(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse(self.view_name_list,
                                           kwargs={"ws_pk": self.ws_1_comment_1.workspace.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_comment_get(self):
        """Test comment get."""
        response = self.client.get(reverse(self.view_name_list,
                                           kwargs={"ws_pk": self.ws_1_comment_1.workspace.pk}))
        response_1 = self.client.get(reverse(self.view_name_detail, kwargs={
            "ws_pk": self.ws_1_comment_1.workspace.pk,
            "pk": self.ws_1_comment_1.pk,
        }))
        comment_1_serializer = self.get_comment_serializers(
            pk_seq=[self.ws_1_comment_1.pk])
        ws_1_serializers = self.get_comment_serializers(
            ws_pk_seq=[self.ws_1_comment_1.workspace.pk])

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ws_1_serializers.data
        assert response_1.data == comment_1_serializer.data[0]

    def test_comment_create_post(self):
        """
        Test comment create post.
        """
        data = {
            "content": "comment tmp",
            "workspace": self.workspace_1.pk,
            "parent": "",
        }
        url = reverse(self.view_name_list, kwargs={
                      "ws_pk": self.ws_1_comment_1.workspace.pk})
        response = self.client.post(url, data)
        retrieved_data = core_models.WorkspaceComment.objects.filter(
            content="comment tmp")
        assert response.status_code == status.HTTP_201_CREATED
        assert retrieved_data.exists()

    def test_comment_update_patch(self):
        """Test comment update using patch."""
        data = {
            "content": "edit 1",
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_comment_1.workspace.pk,
                          "pk": self.ws_1_comment_1.pk,
                      })
        response = self.client.patch(url, data)
        self.ws_1_comment_1.refresh_from_db()
        comment_1_serializer = self.get_comment_serializers(
            pk_seq=[self.ws_1_comment_1.pk])
        assert response.status_code == status.HTTP_200_OK
        assert response.data == comment_1_serializer.data[0]

    def test_comment_update_put(self):
        """Test comment update using put."""
        data = {
            "content": "comment tmp",
            "workspace": self.workspace_1.pk,
            "parent": "",
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_comment_1.workspace.pk,
                          "pk": self.ws_1_comment_1.pk,
                      })
        response = self.client.put(url, data)
        self.ws_1_comment_1.refresh_from_db()
        comment_1_serializer = self.get_comment_serializers(
            pk_seq=[self.ws_1_comment_1.pk])
        assert response.status_code == status.HTTP_200_OK
        assert response.data == comment_1_serializer.data[0]

    def test_comment_delete(self):
        """Test comment delete."""
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_comment_1.workspace.pk,
                          "pk": self.ws_1_comment_1.pk,
                      })
        response = self.client.delete(url)
        comment_1_query = self.get_comment_query(
            pk_seq=[self.ws_1_comment_1.pk])
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.assertFalse(comment_1_query.exists())


class WorkspaceCommentApiConstraintTests(WorkspaceCommentApiFullSetupTestClass):
    """
    Test model constraints.
    """


class WorkspaceCommentApiCleanSaveDeleteTests(WorkspaceCommentApiFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """


class WorkspaceCommentApiTreeTests(WorkspaceCommentApiFullSetupTestClass):
    """
    Test model's tree related
        - validation
        - functionality
    """

    @classmethod
    def db_create_comments_nested(cls, user, workspace):
        setattr(cls,
                f'ws_{workspace.pk}_nested_comment_1',
                core_models.WorkspaceComment.objects.create(
                    content="Nested comment 1",
                    workspace=workspace,
                    created_by=user,
                ))
        setattr(cls,
                f'ws_{workspace.pk}_nested_comment_1_1',
                core_models.WorkspaceComment.objects.create(
                    content="Nested comment 1_1",
                    workspace=workspace,
                    created_by=user,
                    parent=cls.ws_1_nested_comment_1,
                ))
        setattr(cls,
                f'ws_{workspace.pk}_nested_comment_1_1_1',
                core_models.WorkspaceComment.objects.create(
                    content="Nested comment 1_1_1",
                    workspace=workspace,
                    created_by=user,
                    parent=cls.ws_1_nested_comment_1_1,
                ))
        setattr(cls,
                f'ws_{workspace.pk}_nested_comment_1_1_2',
                core_models.WorkspaceComment.objects.create(
                    content="Nested comment 1_1_2",
                    workspace=workspace,
                    created_by=user,
                    parent=cls.ws_1_nested_comment_1_1,
                ))

    @classmethod
    def setUpTestData(cls):
        """
        Create some nested categories in db.
        """
        super().setUpTestData()
        cls.db_create_comments_nested(cls.user, cls.workspace_1)
        cls.db_create_comments_nested(cls.user, cls.workspace_2)

    def test_create_post(self):
        data = {
            "content": "comment tmp",
            "description": "",
            "workspace": self.workspace_1.pk,
            "parent": self.ws_1_nested_comment_1_1.pk,
        }
        url = reverse(self.view_name_list, kwargs={
                      "ws_pk": self.ws_1_nested_comment_1_1.workspace.pk})
        response = self.client.post(url, data)
        retrieved_data = core_models.WorkspaceComment.objects.filter(
            content="comment tmp", parent=self.ws_1_nested_comment_1_1)
        assert response.status_code == status.HTTP_201_CREATED
        assert retrieved_data.exists()

    def test_error_parent_same_on_update_patch(self):
        """
        Test comment parent is not same on update using patch.
        """
        data = {
            "parent": self.ws_1_nested_comment_1_1.pk,
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_nested_comment_1.workspace.pk,
                          "pk": self.ws_1_nested_comment_1_1.pk,
                      })
        response = self.client.patch(url, data)
        self.ws_1_nested_comment_1_1.refresh_from_db()
        comment_1_serializer = self.get_comment_serializers(
            pk_seq=[self.ws_1_nested_comment_1_1.pk])
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Parent cannot be object itself." in response.data[0]

    def test_error_parent_same_on_update_put(self):
        """
        Test comment parent is not same on update using put.
        """
        data = {
            "content": "comment tmp",
            "description": "",
            "workspace": self.ws_1_nested_comment_1_1.workspace.pk,
            "parent": self.ws_1_nested_comment_1_1.pk,
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_nested_comment_1.workspace.pk,
                          "pk": self.ws_1_nested_comment_1_1.pk,
                      })
        response = self.client.put(url, data)
        self.ws_1_nested_comment_1_1.refresh_from_db()
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Parent cannot be object itself." in response.data[0]

    def test_error_parent_workspace_same_on_create_post(self):
        """
        Test comment parent's workspace is same when creating using post.
        Since api does not allow access to different workspace while 
        updating a comment "invalid pk" error is raised.
        """
        data = {
            "content": "comment tmp",
            "description": "",
            "workspace": self.ws_1_nested_comment_1_1.workspace.pk,
            "parent": self.ws_2_nested_comment_1.pk,
        }
        url = reverse(self.view_name_list,
                      kwargs={
                          "ws_pk": self.ws_1_nested_comment_1_1.workspace.pk,
                      })
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_error_parent_workspace_same_on_update_put(self):
        """
        Test comment parent's workspace is same when updating using put.
        Since api does not allow access to different workspace while 
        updating a comment "invalid pk" error is raised.
        """
        data = {
            "content": "comment tmp",
            "description": "",
            "workspace": self.ws_1_nested_comment_1_1.workspace.pk,
            "parent": self.ws_2_nested_comment_1.pk,
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "pk": self.ws_1_nested_comment_1_1.pk,
                          "ws_pk": self.ws_1_nested_comment_1_1.workspace.pk,
                      })
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
