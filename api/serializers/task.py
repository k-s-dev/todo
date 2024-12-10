import re
from rest_framework import serializers
from rest_framework.relations import reverse

from api.serializers import custom_fields
from api.serializers import custom_classes
from api.serializers import category as category_serializers

from core import models as core_models


class CustomTaskTreeHMS(category_serializers.CustomCategoryElementTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS > CustomCategoryElementTreeHMS
    - Used in
        - TaskSerializer
    - Implements
        - fields: workspace, category, tags, priority, status, tree parent with category
    """

    workspace = custom_fields.WorkspacePKRF()
    category = custom_fields.CategoryPKRF()
    project = custom_fields.ProjectPKRF(allow_null=True, required=False)
    tags = custom_fields.TagPKRF(many=True, required=False)
    priority = custom_fields.PriorityPKRF(allow_null=True, required=False)
    status = custom_fields.StatusPKRF(allow_null=True, required=False)
    parent = custom_fields.CustomCategoryElementParentPKRF(allow_null=True, required=False)
    is_visible = serializers.BooleanField(initial=True, required=False)


class CustomProjectTaskTreeHMS(CustomTaskTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS > CustomTaskTreeHMS
    - Used in
        - ProjectTaskSerializer
    - Implements
        - methods:
            - get_reverse_kwargs() for CustomTreeHMS
            - _get_view_name() customized for urls for project tasks view
    """

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.project.workspace.pk,
            "cat_pk": obj.project.category.pk,
            "pr_pk": obj.project.pk,
            "pk": obj.pk,
        }

    def _get_view_name(self):
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        view_name_pre = self.Meta.model.__name__
        view_name_pre = pattern.sub('-', view_name_pre).lower()
        return f'api:project-{view_name_pre}-detail'


class CustomTaskCommentTreeHMS(custom_classes.CustomTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS
    - Used in
        - TaskCommentSerializer
    - Implements
        - fields: task, tree parent with task
        - methods: get_reverse_kwargs() for CustomTreeHMS
    """

    task = custom_fields.TaskPKRF()
    parent = custom_fields.CustomTaskElementParentPKRF(allow_null=True)

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.task.workspace.pk,
            "cat_pk": obj.task.category.pk,
            "task_pk": obj.task.pk,
            "pk": obj.pk,
        }


class ProjectTaskSerializer(CustomProjectTaskTreeHMS):
    url = custom_fields.CustomPrPkHIF(view_name="api:project-task-detail")
    comment_list = serializers.SerializerMethodField(read_only=True)

    def get_comment_list(self, obj):
        return reverse(
            "api:task-comment-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.category.pk,
                "task_pk": obj.pk,
            },
            request=self.context["request"],)

    class Meta:
        model = core_models.Task
        fields = [
            "url", "id", "uuid", "title", "detail",
            "workspace", "category", "project",
            "tags", "status", "priority", "parent", "is_visible",
            "estimated_start_date", "estimated_end_date",
            "actual_start_date", "actual_end_date",
            "estimated_effort", "actual_effort",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url", "comment_list",
        ]


class TaskSerializer(CustomTaskTreeHMS):
    url = custom_fields.CustomCatPkHIF(view_name="api:task-detail")
    comment_list = serializers.SerializerMethodField(read_only=True)

    def get_comment_list(self, obj):
        return reverse(
            "api:task-comment-list",
            kwargs={
                "ws_pk": obj.workspace.pk,
                "cat_pk": obj.category.pk,
                "task_pk": obj.pk,
            },
            request=self.context["request"],)

    class Meta:
        model = core_models.Task
        fields = [
            "url", "id", "uuid", "title", "detail",
            "workspace", "category", "project",
            "tags", "status", "priority", "parent", "is_visible",
            "estimated_start_date", "estimated_end_date",
            "actual_start_date", "actual_end_date",
            "estimated_effort", "actual_effort",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url", "comment_list",
        ]


class TaskCommentSerializer(CustomTaskCommentTreeHMS):
    url = custom_fields.CustomTaskPkHIF(view_name="api:task-comment-detail")

    class Meta:
        model = core_models.TaskComment
        fields = [
            "url", "id", "content", "task", "parent",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url",
        ]
