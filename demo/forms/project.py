from django import forms as djf
from django.db.models import Q

from core import models as core_models
from demo import utils as demo_utils

class ProjectForm(demo_utils.CustomModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance.pk:
            self.fields["workspace"].queryset = core_models.Workspace\
                .objects.filter(pk=self.instance.workspace.pk)
            self.fields["status"].queryset = core_models.Status.objects.filter(
                workspace=self.instance.workspace)
            self.fields["priority"].queryset = core_models.Priority.objects.filter(
                workspace=self.instance.workspace)
            self.fields["tags"].queryset = core_models.Tag.objects.filter(
                workspace=self.instance.workspace)
            self.fields["parent"].queryset = core_models.Project.objects.filter(
                Q(workspace=self.instance.workspace)
                & Q(category=self.instance.category)
                & ~Q(pk=self.instance.pk)
            )
    class Meta:
        model = core_models.Project
        widgets = {
            "estimated_start_date": djf.DateInput(attrs={'type': 'date'}),
            "estimated_end_date": djf.DateInput(attrs={'type': 'date'}),
            "actual_start_date": djf.DateInput(attrs={'type': 'date'}),
            "actual_end_date": djf.DateInput(attrs={'type': 'date'}),
        }
        fields = [
            "title",
            "detail",
            "workspace",
            "category",
            "tags",
            "status",
            "priority",
            "parent",
            "is_visible",
            "estimated_start_date",
            "estimated_end_date",
            "actual_start_date",
            "actual_end_date",
            "estimated_effort",
            "actual_effort"
        ]


class ProjectCommentForm(demo_utils.CustomModelForm):
    class Meta:
        model = core_models.ProjectComment
        fields = ["content", "project", "parent"]



