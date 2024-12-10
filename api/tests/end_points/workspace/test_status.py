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


class StatusApiMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.user = cls.create_user()
        cls.view_name_list = "api:status-list"
        cls.view_name_detail = "api:status-detail"

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
    def get_status_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.Status.objects.all()
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
    def db_create_statuses(cls, user, workspace, multiple=True):
        status_1_attr_name = f'ws_{workspace.pk}_status_1'
        setattr(cls, status_1_attr_name,
                core_models.Status.objects.create(
                    name="status 1",
                    workspace=workspace,
                    created_by=cls.user,
                ))
        if multiple:
            status_2_attr_name = f'ws_{workspace.pk}_status_2'
            setattr(cls, status_2_attr_name,
                    core_models.Status.objects.create(
                        name="status 2",
                        workspace=workspace,
                        created_by=cls.user,
                    ))

    @classmethod
    def get_status_serializers(cls, pk_seq=None, ws_pk_seq=None):
        status_query = cls.get_status_query(pk_seq, ws_pk_seq).order_by("id")
        return api_serializers.StatusSerializer(
            status_query, many=True, context={"request": cls.request_tmp},
        )


class StatusApiFullSetupTestClass(StatusApiMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_statuses(cls.user, workspace)

    def setUp(self):
        super().setUp()


class StatusApiAuthAndCrudTests(StatusApiFullSetupTestClass):
    """Test basic auth and CRUD operations on status view api."""

    def test_auth_required(self):
        self.client.force_authenticate(None)
        response = self.client.get(reverse(self.view_name_list,
                                           kwargs={"ws_pk": self.ws_1_status_1.workspace.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_status_get(self):
        """Test status get."""
        response = self.client.get(reverse(self.view_name_list,
                                           kwargs={"ws_pk": self.ws_1_status_1.workspace.pk}))
        response_1 = self.client.get(reverse(self.view_name_detail, kwargs={
            "ws_pk": self.ws_1_status_1.workspace.pk,
            "pk": self.ws_1_status_1.pk,
        }))
        status_1_serializer = self.get_status_serializers(
            pk_seq=[self.ws_1_status_1.pk])
        ws_1_status_serializers = self.get_status_serializers(
            ws_pk_seq=[self.ws_1_status_1.workspace.pk])

        assert response.status_code == status.HTTP_200_OK
        assert response.data == ws_1_status_serializers.data
        assert response_1.data == status_1_serializer.data[0]

    def test_status_create_post(self):
        """
        Test status create post.
        """
        data = {
            "name": "status tmp",
            "workspace": self.workspace_1.pk,
        }
        url = reverse(self.view_name_list, kwargs={
                      "ws_pk": self.ws_1_status_1.workspace.pk})
        response = self.client.post(url, data)
        retrieved_data = core_models.Status.objects.filter(name="status tmp")
        assert response.status_code == status.HTTP_201_CREATED
        assert retrieved_data.exists()

    def test_status_update_patch(self):
        """Test status update using patch."""
        data = {
            "name": "edit 1",
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_status_1.workspace.pk,
                          "pk": self.ws_1_status_1.pk,
                      })
        response = self.client.patch(url, data)
        self.ws_1_status_1.refresh_from_db()
        status_1_serializer = self.get_status_serializers(
            pk_seq=[self.ws_1_status_1.pk])
        assert response.status_code == status.HTTP_200_OK
        assert response.data == status_1_serializer.data[0]

    def test_status_update_put(self):
        """Test status update using put."""
        data = {
            "name": "default",
            "workspace": self.workspace_1.pk,
        }
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_status_1.workspace.pk,
                          "pk": self.ws_1_status_1.pk,
                      })
        response = self.client.put(url, data)
        self.ws_1_status_1.refresh_from_db()
        status_1_serializer = self.get_status_serializers(
            pk_seq=[self.ws_1_status_1.pk])
        assert response.status_code == status.HTTP_200_OK
        assert response.data == status_1_serializer.data[0]

    def test_status_delete(self):
        """Test status delete."""
        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_status_1.workspace.pk,
                          "pk": self.ws_1_status_1.pk,
                      })
        response = self.client.delete(url)
        status_1_query = self.get_status_query(pk_seq=[self.ws_1_status_1.pk])
        assert response.status_code == status.HTTP_204_NO_CONTENT
        self.assertFalse(status_1_query.exists())


class StatusApiConstraintTests(StatusApiFullSetupTestClass):
    """
    Test model constraints.
    """

    def test_unique_lower_name_workspace_fail_on_duplicate_during_create(self):
        """
        Test that status name is unique for a workspace at time of creation.
        Check that "unique_lower_status_owner_name" error is raised on duplicate.
        """

        url = reverse(self.view_name_list, kwargs={
                      "ws_pk": self.ws_1_status_1.workspace.pk})
        data = {
            "name": "status 1",
            "workspace": self.workspace_1.pk,
        }
        response = self.client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unique_lower_status_name_workspace" in response.data[0]

    def test_unique_lower_name_workspace_fail_on_duplicate_during_update_put(self):
        """
        Test that status name is unique for a workspace at time of update using put.
        Check that "unique_lower_status_owner_name" error is raised on duplicate.
        """

        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_status_1.workspace.pk,
                          "pk": self.ws_1_status_1.pk,
                      })
        data = {
            "name": "status 2",
            "workspace": self.workspace_1.pk,
        }
        response = self.client.put(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unique_lower_status_name_workspace" in response.data[0]

    def test_unique_lower_name_workspace_fail_on_duplicate_during_update_patch(self):
        """
        Test that status name is unique for a workspace at time of update using patch.
        Check that "unique_lower_status_owner_name" error is raised on duplicate.
        """

        url = reverse(self.view_name_detail,
                      kwargs={
                          "ws_pk": self.ws_1_status_1.workspace.pk,
                          "pk": self.ws_1_status_1.pk,
                      })
        data = {
            "name": "status 2",
        }
        response = self.client.patch(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "unique_lower_status_name_workspace" in response.data[0]

    def test_unique_lower_name_workspace_allow_duplicate_for_different_workspace(self):
        """
        Check that duplicate name for different workspaces is allowed.
        """

        duplicate_name = "duplicate status across workspace"
        url_1 = reverse(self.view_name_list,
                        kwargs={"ws_pk": self.ws_1_status_1.workspace.pk, })
        data_1 = {
            "name": duplicate_name,
            "workspace": self.workspace_1.pk,
        }
        url_2 = reverse(self.view_name_list,
                        kwargs={"ws_pk": self.workspace_2.pk, })
        data_2 = {
            "name": duplicate_name,
            "workspace": self.workspace_2.pk,
        }
        response_1 = self.client.post(url_1, data_1)
        response_2 = self.client.post(url_2, data_2)
        assert response_2.status_code == status.HTTP_201_CREATED
        assert "unique_lower_status_name_workspace" not in response_2.data
        assert self.get_status_query().filter(name=duplicate_name).count() == 2


class StatusApiCleanSaveDeleteTests(StatusApiFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """