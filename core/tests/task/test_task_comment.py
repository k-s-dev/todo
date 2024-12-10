from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core import models as core_models
from ..generic_classes import CustomTestCaseSetup


class TaskCommentModelMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    @staticmethod
    def get_comment_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.TaskComment.objects.all()
        if pk_seq:
            qry = qry.filter(pk__in=pk_seq)
        if ws_pk_seq:
            qry = qry.filter(task__pk__in=ws_pk_seq)
        return qry

    @classmethod
    def db_create_comments(cls, user, task, multiple=True):
        comment_1_attr_name = f'task_{task.pk}_comment_1'
        setattr(cls, comment_1_attr_name,
                core_models.TaskComment.objects.create(
                    content="comment 1",
                    task=task,
                    created_by=cls.user,
                ))
        if multiple:
            comment_2_attr_name = f'task_{task.pk}_comment_2'
            setattr(cls, comment_2_attr_name,
                    core_models.TaskComment.objects.create(
                        content="comment 2",
                        task=task,
                        created_by=cls.user,
                    ))


class TaskCommentModelFullSetupTestClass(TaskCommentModelMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_categories(cls.user, workspace)
        for category in cls.get_category_query():
            cls.db_create_tasks(cls.user, category)
        for task in cls.get_task_query():
            cls.db_create_comments(cls.user, task)

    def setUp(self):
        super().setUp()


class TaskCommentModelAuthAndCrudTests(TaskCommentModelFullSetupTestClass):
    """Test basic auth and CRUD operations on comment view api."""

    def test_comment_create(self):
        """
        Test comment create.
        """

        assert self.task_1_comment_1.content == "comment 1"

    def test_comment_read(self):
        """Test comment read."""

        assert self.task_1_comment_1.content == "comment 1"

    def test_comment_update(self):
        """Test comment update using."""

        self.task_1_comment_1.content = "update 1"
        assert self.task_1_comment_1.content == "update 1"

    def test_comment_delete(self):
        """Test comment delete."""

        self.task_1_comment_1.delete()
        self.assertFalse(self.get_comment_query(
            [self.task_1_comment_1.pk]).exists())


class TaskCommentModelConstraintTests(TaskCommentModelFullSetupTestClass):
    """
    Test model constraints.
    """


class TaskCommentModelCleanSaveDeleteTests(TaskCommentModelFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """


class TaskCommentModelTreeTests(TaskCommentModelFullSetupTestClass):
    """
    Test model's tree related
        - validation
        - functionality
    """

    @classmethod
    def db_create_comments_nested(cls, user, task):
        setattr(cls,
                f'task_{task.pk}_nested_comment_1',
                core_models.TaskComment.objects.create(
                    content="Nested comment 1",
                    task=task,
                    created_by=user,
                ))
        setattr(cls,
                f'task_{task.pk}_nested_comment_1_1',
                core_models.TaskComment.objects.create(
                    content="Nested comment 1_1",
                    task=task,
                    created_by=user,
                    parent=cls.task_1_nested_comment_1,
                ))
        setattr(cls,
                f'task_{task.pk}_nested_comment_1_1_1',
                core_models.TaskComment.objects.create(
                    content="Nested comment 1_1_1",
                    task=task,
                    created_by=user,
                    parent=cls.task_1_nested_comment_1_1,
                ))
        setattr(cls,
                f'task_{task.pk}_nested_comment_1_1_2',
                core_models.TaskComment.objects.create(
                    content="Nested comment 1_1_2",
                    task=task,
                    created_by=user,
                    parent=cls.task_1_nested_comment_1_1,
                ))

    @classmethod
    def setUpTestData(cls):
        """
        Create some nested categories in db.
        """
        super().setUpTestData()
        cls.db_create_comments_nested(cls.user, cls.cat_1_task_1)
        cls.db_create_comments_nested(cls.user, cls.cat_1_task_2)

    def test_create(self):
        assert self.task_1_nested_comment_1.content == "Nested comment 1"

    def test_error_parent_same_on_update(self):
        """
        Test comment parent is not same on update.
        """

        msg = "Parent cannot be object itself."
        self.task_1_nested_comment_1_1.parent = self.task_1_nested_comment_1_1
        try:
            self.task_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_task_same_on_create(self):
        """
        Test comment parent's task is same when creating using.
        """

        msg = "Task should be same as parent's."
        try:
            core_models.TaskComment.objects.create(
                content="comment tmp",
                task=self.cat_1_task_1,
                parent=self.task_2_nested_comment_1,
                created_by=self.user,
            )
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_task_same_on_update(self):
        """
        Test comment parent's task is same when updating using put.
        """

        msg = "Task should be same as parent's."
        self.task_1_nested_comment_1_1.parent = self.task_2_nested_comment_1
        try:
            self.task_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)
