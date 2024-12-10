import re
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DrfVE
from rest_framework.relations import reverse
from django.db import IntegrityError, transaction
from django.core.exceptions import ValidationError as DjVE

from api.serializers import custom_fields


class CustomBaseHMS(serializers.HyperlinkedModelSerializer):
    """
    Custom base HyperlinkedModelSerializer which implements the following
    - created_by ReadOnlyField
    - create and updated methods that run model's full_clean
      - trap django exceptions (`ValidationError`, `IntegrityError`)
      - raise rest_framework `ValidationError`
      - update method rolls back django's atomic db transaction in case of error
    """

    created_by = serializers.ReadOnlyField(source="created_by.username")

    def create(self, validated_data):
        user = self.context["request"].user
        validated_data = {
            **validated_data,
            "created_by": user,
        }
        with transaction.atomic(savepoint=True, durable=False):
            try:
                instance_tmp = super().create(validated_data)
                instance_tmp.full_clean()
            except (DjVE, IntegrityError) as e:
                raise DrfVE(e)
            finally:
                transaction.set_rollback(True)
        return super().create(validated_data)

    def update(self, instance, validated_data):
        user = self.context["request"].user
        validated_data = {
            **validated_data,
            "created_by": user,
        }
        with transaction.atomic(savepoint=True, durable=False):
            try:
                instance = super().update(instance, validated_data)
                instance.full_clean()
            except (DjVE, IntegrityError) as e:
                transaction.set_rollback(True)
                raise DrfVE(e)
            except Exception as e:
                transaction.set_rollback(True)
                raise DrfVE(f'Unknown error: {e}')
            else:
                if self.is_valid(raise_exception=True):
                    instance.save()
                    return instance


class CustomTreeHMS(CustomBaseHMS):
    """
    Base HyperlinkedModelSerializer for tree based model serializers to create
    more custom serializers.

    - Inherits from CustomBaseHMS
    - Implements method fields and corresponding methods:
        - parent_url
        - children_url
    - get_reverse_kwargs() method needs to be updated for derived classes
      based on model
    """

    parent_url = serializers.SerializerMethodField(read_only=True,
                                                   allow_null=True,)
    children_url = serializers.SerializerMethodField(read_only=True,
                                                     allow_null=True,)

    @classmethod
    def get_reverse_kwargs(cls, obj):
        return {
            "ws_pk": obj.project.workspace.pk,
            "cat_pk": obj.project.category.pk,
            "pr_pk": obj.project.pk,
            "pk": obj.pk,
        }

    @classmethod
    def _get_children_url(cls, obj, request, view_name):
        result = {}
        children = obj.get_children(obj)
        if children:
            for k, v in children.items():
                result[str(k.pk)] = {}
                if k:
                    result[str(k.pk)]["url"] = reverse(
                        view_name,
                        kwargs=cls.get_reverse_kwargs(k),
                        request=request,
                    )
                if v:
                    result[str(k.pk)]["children_url"] \
                        = cls._get_children_url(k, request, view_name)
        return result

    def _get_view_name(self):
        pattern = re.compile(r'(?<!^)(?=[A-Z])')
        view_name_pre = self.Meta.model.__name__
        view_name_pre = pattern.sub('-', view_name_pre).lower()
        return f'api:{view_name_pre}-detail'

    def get_parent_url(self, obj):
        if obj.parent:
            return reverse(
                self._get_view_name(),
                kwargs=self.get_reverse_kwargs(obj.parent),
                request=self.context["request"],)
        return None

    def get_children_url(self, obj):
        return self._get_children_url(
            obj, self.context["request"], self._get_view_name(),
        )
