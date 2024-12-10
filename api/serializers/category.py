from rest_framework import serializers
from rest_framework.relations import reverse

from api.serializers import custom_fields
from api.serializers import custom_classes
from api.serializers import workspace as workspace_serializers

from core import models as core_models


class CustomCategoryElementTreeHMS(custom_classes.CustomTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS
    - Used in
        - CategoryCommentSerializer
        - custom tree classes
            - CustomProjectTreeHMS
            - CustomTaskTreeHMS
    - Implements
        - fields: category, tree parent with category
        - methods: get_reverse_kwargs for CustomTreeHMS
    """

    category = custom_fields.CategoryPKRF()
    parent = custom_fields.CustomCategoryElementParentPKRF(allow_null=True)

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.category.workspace.pk,
            "cat_pk": obj.category.pk,
            "pk": obj.pk,
        }


class CategorySerializer(workspace_serializers.CustomWsTreeHMS):
    url = custom_fields.CustomWsPkHIF(view_name="api:category-detail")
    comment_list = serializers.SerializerMethodField(read_only=True)
    project_list = serializers.SerializerMethodField(read_only=True)
    task_list = serializers.SerializerMethodField(read_only=True)

    def get_comment_list(self, obj):
        return reverse(
            "api:category-comment-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.pk
            },
            request=self.context["request"],)

    def get_project_list(self, obj):
        return reverse(
            "api:project-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.pk
            },
            request=self.context["request"],)

    def get_task_list(self, obj):
        return reverse(
            "api:task-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.pk
            },
            request=self.context["request"],)

    class Meta:
        model = core_models.Category
        fields = [
            "url", "id", "name", "description", "workspace", "parent",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url",
            "comment_list", "project_list", "task_list",
        ]


class CategoryCommentSerializer(CustomCategoryElementTreeHMS):
    url = custom_fields.CustomCatPkHIF(view_name="api:category-comment-detail")

    class Meta:
        model = core_models.CategoryComment
        fields = [
            "url", "id", "content", "category", "parent",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url",
        ]
