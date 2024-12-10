from rest_framework import serializers
from rest_framework.relations import reverse

from api.serializers import custom_fields
from api.serializers import custom_classes
from api.serializers import category as category_serializers

from core import models as core_models


class CustomProjectTreeHMS(category_serializers.CustomCategoryElementTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS > CustomCategoryElementTreeHMS
    - Used in
        - ProjectSerializer
    - Implements
        - fields: workspace, category, tags, priority, status, tree parent with category
    """

    workspace = custom_fields.WorkspacePKRF()
    category = custom_fields.CategoryPKRF()
    tags = custom_fields.TagPKRF(many=True)
    priority = custom_fields.PriorityPKRF(allow_null=True, required=False)
    status = custom_fields.StatusPKRF(allow_null=True, required=False)
    parent = custom_fields.CustomCategoryElementParentPKRF(allow_null=True, required=False)
    is_visible = serializers.BooleanField(initial=True, required=False)


class CustomProjectCommentTreeHMS(custom_classes.CustomTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS
    - Used in
        - ProjectCommentSerializer
    - Implements
        - fields: project, tree parent with project
        - methods: get_reverse_kwargs() for CustomTreeHMS
    """

    project = custom_fields.ProjectPKRF()
    parent = custom_fields.CustomProjectElementParentPKRF(allow_null=True)

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.project.workspace.pk,
            "cat_pk": obj.project.category.pk,
            "pr_pk": obj.project.pk,
            "pk": obj.pk,
        }


class ProjectSerializer(CustomProjectTreeHMS):
    url = custom_fields.CustomCatPkHIF(view_name="api:project-detail")
    comment_list = serializers.SerializerMethodField(read_only=True)
    task_list = serializers.SerializerMethodField(read_only=True)

    def get_comment_list(self, obj):
        return reverse(
            "api:project-comment-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.category.pk,
                "pr_pk": obj.pk,
            },
            request=self.context["request"],)

    def get_task_list(self, obj):
        return reverse(
            "api:project-task-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.category.pk,
                "pr_pk": obj.pk,
            },
            request=self.context["request"],)

    class Meta:
        model = core_models.Project
        fields = [
            "url", "id", "uuid", "title", "detail", "workspace", "category",
            "tags", "status", "priority", "parent", "is_visible",
            "estimated_start_date", "estimated_end_date",
            "actual_start_date", "actual_end_date",
            "estimated_effort", "actual_effort",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url", "comment_list", "task_list",
        ]


class ProjectCommentSerializer(CustomProjectCommentTreeHMS):
    url = custom_fields.CustomPrPkHIF(view_name="api:project-comment-detail")

    class Meta:
        model = core_models.ProjectComment
        fields = [
            "url", "id", "content", "project", "parent",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url",
        ]
