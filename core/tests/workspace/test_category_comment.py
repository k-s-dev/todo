from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from core import models as core_models
from ..generic_classes import CustomTestCaseSetup


class CategoryCommentModelMinimalSetupClass(CustomTestCaseSetup):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()

    def setUp(self):
        super().setUp()

    @staticmethod
    def get_comment_query(pk_seq=None, ws_pk_seq=None):
        qry = core_models.CategoryComment.objects.all()
        if pk_seq:
            qry = qry.filter(pk__in=pk_seq)
        if ws_pk_seq:
            qry = qry.filter(category__pk__in=ws_pk_seq)
        return qry

    @classmethod
    def db_create_comments(cls, user, category, multiple=True):
        comment_1_attr_name = f'cat_{category.pk}_comment_1'
        setattr(cls, comment_1_attr_name,
                core_models.CategoryComment.objects.create(
                    content="comment 1",
                    category=category,
                    created_by=cls.user,
                ))
        if multiple:
            comment_2_attr_name = f'cat_{category.pk}_comment_2'
            setattr(cls, comment_2_attr_name,
                    core_models.CategoryComment.objects.create(
                        content="comment 2",
                        category=category,
                        created_by=cls.user,
                    ))


class CategoryCommentModelFullSetupTestClass(CategoryCommentModelMinimalSetupClass):
    @classmethod
    def setUpTestData(cls):
        super().setUpTestData()
        cls.db_create_workspaces(cls.user)
        for workspace in cls.get_workspace_query():
            cls.db_create_categories(cls.user, workspace)
        for category in cls.get_category_query():
            cls.db_create_comments(cls.user, category)

    def setUp(self):
        super().setUp()


class CategoryCommentModelAuthAndCrudTests(CategoryCommentModelFullSetupTestClass):
    """Test basic auth and CRUD operations on comment view api."""

    def test_comment_create(self):
        """
        Test comment create.
        """

        assert self.cat_1_comment_1.content == "comment 1"

    def test_comment_read(self):
        """Test comment read."""

        assert self.cat_1_comment_1.content == "comment 1"

    def test_comment_update(self):
        """Test comment update using."""

        self.cat_1_comment_1.content = "update 1"
        assert self.cat_1_comment_1.content == "update 1"

    def test_comment_delete(self):
        """Test comment delete."""

        self.cat_1_comment_1.delete()
        self.assertFalse(self.get_comment_query(
            [self.cat_1_comment_1.pk]).exists())


class CategoryCommentModelConstraintTests(CategoryCommentModelFullSetupTestClass):
    """
    Test model constraints.
    """


class CategoryCommentModelCleanSaveDeleteTests(CategoryCommentModelFullSetupTestClass):
    """
    Test model's `clean`, `save`, `delete` methods
        - validation
        - functionality
    """


class CategoryCommentModelTreeTests(CategoryCommentModelFullSetupTestClass):
    """
    Test model's tree related
        - validation
        - functionality
    """

    @classmethod
    def db_create_comments_nested(cls, user, category):
        setattr(cls,
                f'cat_{category.pk}_nested_comment_1',
                core_models.CategoryComment.objects.create(
                    content="Nested comment 1",
                    category=category,
                    created_by=user,
                ))
        setattr(cls,
                f'cat_{category.pk}_nested_comment_1_1',
                core_models.CategoryComment.objects.create(
                    content="Nested comment 1_1",
                    category=category,
                    created_by=user,
                    parent=cls.cat_1_nested_comment_1,
                ))
        setattr(cls,
                f'cat_{category.pk}_nested_comment_1_1_1',
                core_models.CategoryComment.objects.create(
                    content="Nested comment 1_1_1",
                    category=category,
                    created_by=user,
                    parent=cls.cat_1_nested_comment_1_1,
                ))
        setattr(cls,
                f'cat_{category.pk}_nested_comment_1_1_2',
                core_models.CategoryComment.objects.create(
                    content="Nested comment 1_1_2",
                    category=category,
                    created_by=user,
                    parent=cls.cat_1_nested_comment_1_1,
                ))

    @classmethod
    def setUpTestData(cls):
        """
        Create some nested categories in db.
        """
        super().setUpTestData()
        cls.db_create_comments_nested(cls.user, cls.ws_1_category_1)
        cls.db_create_comments_nested(cls.user, cls.ws_1_category_2)

    def test_create(self):
        assert self.cat_1_nested_comment_1.content == "Nested comment 1"

    def test_error_parent_same_on_update(self):
        """
        Test comment parent is not same on update.
        """

        msg = "Parent cannot be object itself."
        self.cat_1_nested_comment_1_1.parent = self.cat_1_nested_comment_1_1
        try:
            self.cat_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_category_same_on_create(self):
        """
        Test comment parent's category is same when creating using.
        """

        msg = "Category should be same as parent's."
        try:
            core_models.CategoryComment.objects.create(
                content="comment tmp",
                category=self.ws_1_category_1,
                parent=self.cat_2_nested_comment_1,
                created_by=self.user,
            )
        except ValidationError as e:
            assert msg in str(e)

    def test_error_parent_category_same_on_update(self):
        """
        Test comment parent's category is same when updating using put.
        """

        msg = "Category should be same as parent's."
        self.cat_1_nested_comment_1_1.parent = self.cat_2_nested_comment_1
        try:
            self.cat_1_nested_comment_1_1.full_clean()
        except ValidationError as e:
            assert msg in str(e)
