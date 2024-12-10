from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core import models as core_models
from ..generic_classes import CustomTestCaseSetup


class WorkspaceCommentModelMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    @staticmethod
    def get_comment_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.WorkspaceComment.objects.all()
        if pk_seq:
            qry = qry.filter(pk__in=pk_seq)
        if ws_pk_seq:
            qry = qry.filter(workspace__pk__in=ws_pk_seq)
        return qry

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


class WorkspaceCommentModelFullSetupTestClass(WorkspaceCommentModelMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_comments(cls.user, workspace)

    def setUp(self):
        super().setUp()


class WorkspaceCommentModelAuthAndCrudTests(WorkspaceCommentModelFullSetupTestClass):
    """Test basic auth and CRUD operations on comment view api."""

    def test_comment_create(self):
        """
        Test comment create.
        """

        assert self.ws_1_comment_1.content == "comment 1"

    def test_comment_read(self):
        """Test comment read."""

        assert self.ws_1_comment_1.content == "comment 1"

    def test_comment_update(self):
        """Test comment update using."""

        self.ws_1_comment_1.content = "update 1"
        assert self.ws_1_comment_1.content == "update 1"

    def test_comment_delete(self):
        """Test comment delete."""

        self.ws_1_comment_1.delete()
        self.assertFalse(self.get_comment_query(
            [self.ws_1_comment_1.pk]).exists())


class WorkspaceCommentModelConstraintTests(WorkspaceCommentModelFullSetupTestClass):
    """
    Test model constraints.
    """


class WorkspaceCommentModelCleanSaveDeleteTests(WorkspaceCommentModelFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """


class WorkspaceCommentModelTreeTests(WorkspaceCommentModelFullSetupTestClass):
    """
    Test model's tree related
        - validation
        - functionality
    """

    msg = "Workspace should be same as parent's."

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

    def test_create(self):
        assert self.ws_1_nested_comment_1.content == "Nested comment 1"

    def test_error_parent_same_on_update(self):
        """
        Test comment parent is not same on update.
        """

        msg = "Parent cannot be object itself."
        self.ws_1_nested_comment_1_1.parent = self.ws_1_nested_comment_1_1
        try:
            self.ws_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_workspace_same_on_create(self):
        """
        Test comment parent's workspace is same when creating using.
        """

        try:
            core_models.WorkspaceComment.objects.create(
                content="comment tmp",
                workspace=self.workspace_1,
                parent=self.ws_2_nested_comment_1,
                created_by=self.user,
            )
        except ValidationError as e:
            assert self.msg in str(e)

    def test_error_parent_workspace_same_on_update(self):
        """
        Test comment parent's workspace is same when updating using put.
        """

        self.ws_1_nested_comment_1_1.parent = self.ws_2_nested_comment_1
        try:
            self.ws_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert self.msg in str(e)
