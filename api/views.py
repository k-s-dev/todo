from django.core.exceptions import ValidationError as DjVE
from rest_framework.exceptions import ValidationError as DrfVE
from django.shortcuts import render
from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import viewsets, permissions

from core import models as core_models
from api.serializers import workspace as workspace_serializers
from api.serializers import category as category_serializers
from api.serializers import project as project_serializers
from api.serializers import task as task_serializers
from . import permissions as api_permissions


User = get_user_model()


class CustomBaseModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            created_by=self.request.user,
        )


class CustomBaseWsModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            workspace__pk=self.kwargs["ws_pk"],
            created_by=self.request.user,
        )


class CustomBaseCatModelViewSet(viewsets.ModelViewSet):
    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            category__pk=self.kwargs["cat_pk"],
            created_by=self.request.user,
        )


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = workspace_serializers.UserSerializer
    permission_classes = [
        permissions.IsAuthenticated,
    ]


class WorkspaceViewSet(CustomBaseModelViewSet):
    serializer_class = workspace_serializers.WorkspaceSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class WorkspaceCommentViewSet(CustomBaseWsModelViewSet):
    serializer_class = workspace_serializers.WorkspaceCommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class CategoryViewSet(CustomBaseWsModelViewSet):
    serializer_class = category_serializers.CategorySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class CategoryCommentViewSet(CustomBaseCatModelViewSet):
    serializer_class = category_serializers.CategoryCommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class TagViewSet(CustomBaseWsModelViewSet):
    serializer_class = workspace_serializers.TagSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class PriorityViewSet(CustomBaseWsModelViewSet):
    serializer_class = workspace_serializers.PrioritySerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class StatusViewSet(CustomBaseWsModelViewSet):
    serializer_class = workspace_serializers.StatusSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class ProjectViewSet(CustomBaseCatModelViewSet):
    serializer_class = project_serializers.ProjectSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class ProjectCommentViewSet(viewsets.ModelViewSet):
    serializer_class = project_serializers.ProjectCommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            project__pk=self.kwargs["pr_pk"],
            created_by=self.request.user,
        )


class ProjectTaskViewSet(viewsets.ModelViewSet):
    serializer_class = task_serializers.ProjectTaskSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            project__pk=self.kwargs["pr_pk"],
            created_by=self.request.user,
        )


class TaskViewSet(CustomBaseCatModelViewSet):
    serializer_class = task_serializers.TaskSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]


class TaskCommentViewSet(viewsets.ModelViewSet):
    serializer_class = task_serializers.TaskCommentSerializer
    permission_classes = [
        permissions.IsAuthenticated,
        api_permissions.IsOwnerOrAdminOrReadOnly,
    ]

    def get_queryset(self):
        return self.serializer_class.Meta.model.objects.filter(
            task__pk=self.kwargs["task_pk"],
            created_by=self.request.user,
        )
