from rest_framework import serializers
from rest_framework.relations import reverse

from core import models as core_models


class WorkspacePKRF(serializers.PrimaryKeyRelatedField):
    """
    Workspace PrimaryKeyRelatedField to be used in all model serializers
    with workspace field.
    get_queryset filters for view's workspace.
    """

    view_name = "api:workspace-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user = request.user
            request_kwargs = request.parser_context.get("kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Workspace.objects.filter(
            created_by=user,
            pk=request_kwargs["ws_pk"]
        )


class TagPKRF(serializers.PrimaryKeyRelatedField):
    """
    Tag PrimaryKeyRelatedField to be used in all model serializers
    with tag field.
    get_queryset filters for view's workspace.
    """

    view_name = "api:tag-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user = request.user
            request_kwargs = request.parser_context.get("kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Tag.objects.filter(
            created_by=user,
            workspace__pk=request_kwargs["ws_pk"]
        )


class PriorityPKRF(serializers.PrimaryKeyRelatedField):
    """
    Priority PrimaryKeyRelatedField to be used in all model serializers
    with priority field.
    get_queryset filters for view's workspace.
    """

    view_name = "api:priority-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user = request.user
            request_kwargs = request.parser_context.get("kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Priority.objects.filter(
            created_by=user,
            workspace__pk=request_kwargs["ws_pk"]
        )


class StatusPKRF(serializers.PrimaryKeyRelatedField):
    """
    Status PrimaryKeyRelatedField to be used in all model serializers
    with status field.
    get_queryset filters for view's workspace and category.
    """

    view_name = "api:status-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user = request.user
            request_kwargs = request.parser_context.get("kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Status.objects.filter(
            created_by=user,
            workspace__pk=request_kwargs["ws_pk"]
        )


class CategoryPKRF(serializers.PrimaryKeyRelatedField):
    """
    Category PrimaryKeyRelatedField to be used in all model serializers
    with category field.
    get_queryset filters for view's workspace and category.
    """

    view_name = "api:category-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user = request.user
            request_kwargs = request.parser_context.get("kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Category.objects.filter(
            created_by=user,
            pk=request_kwargs["cat_pk"]
        )


class ProjectPKRF(serializers.PrimaryKeyRelatedField):
    """
    Project PrimaryKeyRelatedField to be used in all model serializers
    with project field.
    get_queryset filters for view's workspace and category.
    """

    view_name = "api:project-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user, request_kwargs = request.user, request.parser_context.get(
                "kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Project.objects.filter(
            created_by=user,
            category__pk=request_kwargs["cat_pk"]
        )


class TaskPKRF(serializers.PrimaryKeyRelatedField):
    """
    Task PrimaryKeyRelatedField to be used in all model serializers
    with task field.
    get_queryset filters for view's workspace and category.
    """
    view_name = "api:task-detail"

    def get_queryset(self):
        request = self.context.get("request", None)
        if request:
            user, request_kwargs = request.user, request.parser_context.get(
                "kwargs")
        else:
            user, request_kwargs = None, {"ws_pk": None, "cat_pk": None}
        return core_models.Task.objects.filter(
            created_by=user,
            category__pk=request_kwargs["cat_pk"],
            pk=request_kwargs["task_pk"],
        )


class CustomWorkspaceElementParentPKRF(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request", None)
        request_kwargs = request.parser_context.get("kwargs")
        return self.parent.Meta.model.objects.filter(
            created_by=self.context["request"].user,
            workspace__pk=request_kwargs["ws_pk"],
        )


class CustomCategoryElementParentPKRF(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request", None)
        request_kwargs = request.parser_context.get("kwargs")
        return self.parent.Meta.model.objects.filter(
            created_by=self.context["request"].user,
            category__pk=request_kwargs["cat_pk"],
        )


class CustomProjectElementParentPKRF(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request", None)
        request_kwargs = request.parser_context.get("kwargs")
        return self.parent.Meta.model.objects.filter(
            created_by=self.context["request"].user,
            project__pk=request_kwargs["pr_pk"],
        )


class CustomTaskElementParentPKRF(serializers.PrimaryKeyRelatedField):
    def get_queryset(self):
        request = self.context.get("request", None)
        request_kwargs = request.parser_context.get("kwargs")
        return self.parent.Meta.model.objects.filter(
            created_by=self.context["request"].user,
            task__pk=request_kwargs["task_pk"],
        )


class CustomWsPkHIF(serializers.HyperlinkedIdentityField):
    """
    HyperlinkedIdentityField for model serializers with workspace field.
    Allows filtering of get_queryset based on workspace primary key (ws_pk)
    from request kwargs.
    - WorkspaceCommentSerializer
    - TagSerializer
    - PrioritySerializer
    - StatusSerializer
    - CategorySerializer
    e.g. workspace/1/tag
    """

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "ws_pk": obj.workspace.pk,
            "pk": obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            "ws_pk": view_kwargs["ws_pk"],
            "pk": view_kwargs["pk"],
        }
        return self.get_queryset().get(**lookup_kwargs)


class CustomCatPkHIF(serializers.HyperlinkedIdentityField):
    """
    HyperlinkedIdentityField for model serializers with category field.
    Allows filtering of get_queryset based on category primary key (cat_pk)
    from request kwargs.
    - CategoryCommentSerializer
    - ProjectSerializer
    - TaskSerializer
    e.g. workspace/1/category/1/task
    """

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "ws_pk": obj.category.workspace.pk,
            "cat_pk": obj.category.pk,
            "pk": obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            "category": view_kwargs["cat_pk"],
            "pk": view_kwargs["pk"],
        }
        return self.get_queryset().get(**lookup_kwargs)


class CustomPrPkHIF(serializers.HyperlinkedIdentityField):
    """
    HyperlinkedIdentityField for model serializers with project field.
    Allows filtering of get_queryset based on project primary key (pr_pk)
    from request kwargs.
    - ProjectTaskSerializer
    - ProjectCommentSerializer
    e.g. workspace/1/category/1/project/1/task
    """

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "ws_pk": obj.project.workspace.pk,
            "cat_pk": obj.project.category.pk,
            "pr_pk": obj.project.pk,
            "pk": obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            "workspace": view_kwargs["ws_pk"],
            "category": view_kwargs["cat_pk"],
            "project": view_kwargs["pr_pk"],
            "pk": view_kwargs["pk"],
        }
        return self.get_queryset().get(**lookup_kwargs)


class CustomTaskPkHIF(serializers.HyperlinkedIdentityField):
    """
    HyperlinkedIdentityField for model serializers with task field.
    Allows filtering of get_queryset based on task primary key (task_pk)
    from request kwargs.
    - TaskCommentSerializer
    e.g. workspace/1/category/1/project/1/task/1/comment
    """

    def get_url(self, obj, view_name, request, format):
        url_kwargs = {
            "ws_pk": obj.task.workspace.pk,
            "cat_pk": obj.task.category.pk,
            "task_pk": obj.task.pk,
            "pk": obj.pk,
        }
        return reverse(view_name, kwargs=url_kwargs, request=request, format=format)

    def get_object(self, view_name, view_args, view_kwargs):
        lookup_kwargs = {
            "workspace": view_kwargs["ws_pk"],
            "category": view_kwargs["cat_pk"],
            "task": view_kwargs["task_pk"],
            "pk": view_kwargs["pk"],
        }
        return self.get_queryset().get(**lookup_kwargs)
