from django.forms import ModelForm

from core import models as core_models
from demo import utils as demo_utils


class WorkspaceCommentForm(demo_utils.CustomModelForm):
    class Meta:
        model = core_models.WorkspaceComment
        fields = ["content", "workspace", "parent"]


class CategoryCommentForm(demo_utils.CustomModelForm):
    class Meta:
        model = core_models.CategoryComment
        fields = ["content", "category", "parent"]
