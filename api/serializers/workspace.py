from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.relations import reverse

from api.serializers import custom_fields
from api.serializers import custom_classes

from core import models as core_models


class CustomWsHMS(custom_classes.CustomBaseHMS):
    """
    Custom HyperlinkedModelSerializer for workspace related serializers like
    tag, priority and status.
    """
    workspace = custom_fields.WorkspacePKRF()


class CustomWsTreeHMS(custom_classes.CustomTreeHMS):
    """
    - Inherits from CustomBaseHMS > CustomTreeHMS
    - Used in
        - WorkspaceCommentSerializer
        - CategorySerializer
    - Implements
        - fields: workspace, tree parent with workspace
        - methods: get_reverse_kwargs for CustomTreeHMS
    """

    workspace = custom_fields.WorkspacePKRF()
    parent = custom_fields.CustomWorkspaceElementParentPKRF(allow_null=True)

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.workspace.pk,
            "pk": obj.pk,
        }


class UserSerializer(serializers.HyperlinkedModelSerializer):
    url = serializers.HyperlinkedIdentityField(view_name="api:user-detail")
    workspaces = serializers.HyperlinkedRelatedField(
        view_name="api:workspace-detail",
        many=True,
        read_only=True,
    )

    class Meta:
        model = get_user_model()
        fields = [
            "url", "id", "username", "email", "workspaces",
        ]


class WorkspaceSerializer(custom_classes.CustomBaseHMS):
    url = serializers.HyperlinkedIdentityField(
        view_name="api:workspace-detail")
    tag_list = serializers.SerializerMethodField(read_only=True)
    priority_list = serializers.SerializerMethodField(read_only=True)
    status_list = serializers.SerializerMethodField(read_only=True)
    category_list = serializers.SerializerMethodField(read_only=True)
    comment_list = serializers.SerializerMethodField(read_only=True)

    def get_tag_list(self, obj):
        return reverse(
            "api:tag-list",
            kwargs={
                "ws_pk": obj.pk,
            },
            request=self.context["request"],)

    def get_priority_list(self, obj):
        return reverse(
            "api:priority-list",
            kwargs={
                "ws_pk": obj.pk,
            },
            request=self.context["request"],)

    def get_status_list(self, obj):
        return reverse(
            "api:status-list",
            kwargs={
                "ws_pk": obj.pk,
            },
            request=self.context["request"],)

    def get_category_list(self, obj):
        return reverse(
            "api:category-list",
            kwargs={
                "ws_pk": obj.pk,
            },
            request=self.context["request"],)

    def get_comment_list(self, obj):
        return reverse(
            "api:workspace-comment-list",
            kwargs={
                "ws_pk": obj.pk,
            },
            request=self.context["request"],)

    class Meta:
        model = core_models.Workspace
        fields = [
            "url", "id", "name", "description", "is_default",
            "created_by", "created_at", "updated_at",
            "tag_list", "priority_list", "status_list", "category_list",
            "comment_list",
        ]


class WorkspaceCommentSerializer(CustomWsTreeHMS):
    url = custom_fields.CustomWsPkHIF(view_name="api:workspace-comment-detail")

    class Meta:
        model = core_models.WorkspaceComment
        fields = [
            "url", "id", "content", "workspace", "parent",
            "created_by", "created_at", "updated_at",
            "parent_url", "children_url",
        ]


class TagSerializer(CustomWsHMS):
    url = custom_fields.CustomWsPkHIF(view_name="api:tag-detail")

    class Meta:
        model = core_models.Tag
        fields = [
            "url", "id", "name", "workspace",
            "created_by", "created_at", "updated_at"
        ]


class PrioritySerializer(CustomWsHMS):
    url = custom_fields.CustomWsPkHIF(view_name="api:priority-detail")

    class Meta:
        model = core_models.Priority
        fields = [
            "url", "id", "name", "description", "order", "workspace",
            "created_by", "created_at", "updated_at"
        ]


class StatusSerializer(CustomWsHMS):
    url = custom_fields.CustomWsPkHIF(view_name="api:status-detail")

    class Meta:
        model = core_models.Status
        fields = [
            "url", "id", "name", "description", "order", "workspace",
            "created_by", "created_at", "updated_at",
        ]


