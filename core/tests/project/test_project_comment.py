from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core import models as core_models
from ..generic_classes import CustomTestCaseSetup


class ProjectCommentModelMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    @staticmethod
    def get_comment_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.ProjectComment.objects.all()
        if pk_seq:
            qry = qry.filter(pk__in=pk_seq)
        if ws_pk_seq:
            qry = qry.filter(project__pk__in=ws_pk_seq)
        return qry

    @classmethod
    def db_create_comments(cls, user, project, multiple=True):
        comment_1_attr_name = f'pr_{project.pk}_comment_1'
        setattr(cls, comment_1_attr_name,
                core_models.ProjectComment.objects.create(
                    content="comment 1",
                    project=project,
                    created_by=cls.user,
                ))
        if multiple:
            comment_2_attr_name = f'pr_{project.pk}_comment_2'
            setattr(cls, comment_2_attr_name,
                    core_models.ProjectComment.objects.create(
                        content="comment 2",
                        project=project,
                        created_by=cls.user,
                    ))


class ProjectCommentModelFullSetupTestClass(ProjectCommentModelMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_categories(cls.user, workspace)
        for category in cls.get_category_query():
            cls.db_create_projects(cls.user, category)
        for project in cls.get_project_query():
            cls.db_create_comments(cls.user, project)

    def setUp(self):
        super().setUp()


class ProjectCommentModelAuthAndCrudTests(ProjectCommentModelFullSetupTestClass):
    """Test basic auth and CRUD operations on comment view api."""

    def test_comment_create(self):
        """
        Test comment create.
        """

        assert self.pr_1_comment_1.content == "comment 1"

    def test_comment_read(self):
        """Test comment read."""

        assert self.pr_1_comment_1.content == "comment 1"

    def test_comment_update(self):
        """Test comment update using."""

        self.pr_1_comment_1.content = "update 1"
        assert self.pr_1_comment_1.content == "update 1"

    def test_comment_delete(self):
        """Test comment delete."""

        self.pr_1_comment_1.delete()
        self.assertFalse(self.get_comment_query(
            [self.pr_1_comment_1.pk]).exists())


class ProjectCommentModelConstraintTests(ProjectCommentModelFullSetupTestClass):
    """
    Test model constraints.
    """


class ProjectCommentModelCleanSaveDeleteTests(ProjectCommentModelFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """


class ProjectCommentModelTreeTests(ProjectCommentModelFullSetupTestClass):
    """
    Test model's tree related
        - validation
        - functionality
    """

    @classmethod
    def db_create_comments_nested(cls, user, project):
        setattr(cls,
                f'pr_{project.pk}_nested_comment_1',
                core_models.ProjectComment.objects.create(
                    content="Nested comment 1",
                    project=project,
                    created_by=user,
                ))
        setattr(cls,
                f'pr_{project.pk}_nested_comment_1_1',
                core_models.ProjectComment.objects.create(
                    content="Nested comment 1_1",
                    project=project,
                    created_by=user,
                    parent=cls.pr_1_nested_comment_1,
                ))
        setattr(cls,
                f'pr_{project.pk}_nested_comment_1_1_1',
                core_models.ProjectComment.objects.create(
                    content="Nested comment 1_1_1",
                    project=project,
                    created_by=user,
                    parent=cls.pr_1_nested_comment_1_1,
                ))
        setattr(cls,
                f'pr_{project.pk}_nested_comment_1_1_2',
                core_models.ProjectComment.objects.create(
                    content="Nested comment 1_1_2",
                    project=project,
                    created_by=user,
                    parent=cls.pr_1_nested_comment_1_1,
                ))

    @classmethod
    def setUpTestData(cls):
        """
        Create some nested categories in db.
        """
        super().setUpTestData()
        cls.db_create_comments_nested(cls.user, cls.cat_1_project_1)
        cls.db_create_comments_nested(cls.user, cls.cat_1_project_2)

    def test_create(self):
        assert self.pr_1_nested_comment_1.content == "Nested comment 1"

    def test_error_parent_same_on_update(self):
        """
        Test comment parent is not same on update.
        """

        msg = "Parent cannot be object itself."
        self.pr_1_nested_comment_1_1.parent = self.pr_1_nested_comment_1_1
        try:
            self.pr_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_project_same_on_create(self):
        """
        Test comment parent's project is same when creating using.
        """

        msg = "Project should be same as parent's."
        try:
            core_models.ProjectComment.objects.create(
                content="comment tmp",
                project=self.cat_1_project_1,
                parent=self.pr_2_nested_comment_1,
                created_by=self.user,
            )
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_project_same_on_update(self):
        """
        Test comment parent's project is same when updating using put.
        """

        msg = "Project should be same as parent's."
        self.pr_1_nested_comment_1_1.parent = self.pr_2_nested_comment_1
        try:
            self.pr_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)
