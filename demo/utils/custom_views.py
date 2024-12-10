from django.core.exceptions import PermissionDenied
from django.views.generic import edit as djev
from django.urls import reverse, reverse_lazy

from core import models as core_models
from demo import utils as demo_utils


class CustomWsCreateView(djev.CreateView):
    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        cat_pk = params.get("cat_pk", None)
        if ws_pk and not cat_pk:
            ws_pk = int(ws_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            demo_utils.update_context_main(
                self.request, context, workspace.name)
        if ws_pk and cat_pk:
            ws_pk = int(ws_pk[0])
            cat_pk = int(cat_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            category = core_models.Category.objects.get(pk=cat_pk)
            demo_utils.update_context_main(self.request, context, workspace.name,
                                           category.name)
        return context

    def get_form_class(self):
        model_form = super().get_form_class()
        model_form.base_fields["workspace"].limit_choices_to = {
            "created_by": self.request.user}
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        tree_models = [
            core_models.Category,
        ]
        if ws_pk and self.model in tree_models:
            ws_pk = int(ws_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            model_form.base_fields["parent"].limit_choices_to = {
                "created_by": self.request.user,
                "workspace": workspace,
            }
        return model_form

    def get_initial(self):
        initial = super().get_initial()
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        if ws_pk:
            ws_pk = int(ws_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            initial.update({
                "workspace": workspace,
            })
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)


class CustomWsUpdateView(djev.UpdateView):
    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().workspace.created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        cat_pk = params.get("cat_pk", None)
        if ws_pk and not cat_pk:
            ws_pk = int(ws_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            demo_utils.update_context_main(
                self.request, context, workspace.name)
        if ws_pk and cat_pk:
            ws_pk = int(ws_pk[0])
            cat_pk = int(cat_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            category = core_models.Category.objects.get(pk=cat_pk)
            demo_utils.update_context_main(self.request, context, workspace.name,
                                           category.name)
        return context


class CustomWsDeleteView(djev.DeleteView):
    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().workspace.created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        cat_pk = params.get("cat_pk", None)
        if ws_pk and not cat_pk:
            ws_pk = int(ws_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            demo_utils.update_context_main(
                self.request, context, workspace.name)
        if ws_pk and cat_pk:
            ws_pk = int(ws_pk[0])
            cat_pk = int(cat_pk[0])
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            category = core_models.Category.objects.get(pk=cat_pk)
            demo_utils.update_context_main(self.request, context, workspace.name,
                                           category.name)
        return context


class CustomCreateView(djev.CreateView):
    def get_details(self):
        params = dict(self.request.GET)
        ws_pk = params.get("ws_pk", None)
        cat_pk = params.get("cat_pk", None)
        if ws_pk and ws_pk[0]:
            ws_pk = int(ws_pk[0])
        else:
            ws_pk = None
        if cat_pk and cat_pk[0]:
            cat_pk = int(cat_pk[0])
        else:
            cat_pk = None
        return ws_pk, cat_pk

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_pk, cat_pk = self.get_details()
        if ws_pk and not cat_pk:
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            demo_utils.update_context_main(
                self.request, context, workspace.name)
        if ws_pk and cat_pk:
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            category = core_models.Category.objects.get(pk=cat_pk)
            demo_utils.update_context_main(self.request, context, workspace.name,
                                           category.name)
        return context

    def get_form_class(self):
        model_form = super().get_form_class()
        model_form.base_fields["workspace"].limit_choices_to = {
            "created_by": self.request.user}
        ws_pk, cat_pk = self.get_details()
        tree_models = [
            core_models.Task,
            core_models.Project,
        ]
        if ws_pk and not cat_pk and self.model in tree_models:
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            model_form.base_fields["parent"].limit_choices_to = {
                "created_by": self.request.user,
                "workspace": workspace,
            }
            model_form.base_fields["category"].limit_choices_to = {
                "created_by": self.request.user,
                "workspace": workspace,
            }
        if ws_pk and cat_pk and self.model in tree_models:
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            category = core_models.Category.objects.get(pk=cat_pk)
            model_form.base_fields["parent"].limit_choices_to = {
                "created_by": self.request.user,
                "workspace": workspace,
                "category": category,
            }
        return model_form

    def get_initial(self):
        initial = super().get_initial()
        ws_pk, cat_pk = self.get_details()
        if ws_pk:
            workspace = core_models.Workspace.objects.get(pk=ws_pk)
            initial.update({"workspace": workspace})
        if cat_pk:
            category = core_models.Category.objects.get(pk=cat_pk)
            initial.update({"category": category})
        return initial

    def form_valid(self, form):
        form.instance.created_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("demo:category-detail", kwargs={
            "cat_pk": self.object.category.pk
        })


class CustomDeleteView(djev.DeleteView):
    slug_field = "uuid"
    slug_url_kwarg = "uuid"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.workspace.name
        cat_name = self.object.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context

    def get_success_url(self):
        return reverse_lazy("demo:category-detail", kwargs={
            "cat_pk": self.object.category.pk
        })
