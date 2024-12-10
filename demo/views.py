from django.core.checks import messages
from django.core.exceptions import PermissionDenied
from django.forms import ValidationError
from django.http.response import HttpResponseRedirect
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import edit as djev
from django.contrib.auth.forms import UserCreationForm
from django.urls import reverse_lazy
from django.db.models import Q

from core import models as core_models
from demo import utils as demo_utils
from demo import forms as demo_forms


class SignUpView(djev.CreateView):
    form_class = UserCreationForm
    success_url = reverse_lazy("login")
    template_name = "registration/signup.html"


class WorkspaceCreateView(LoginRequiredMixin, djev.CreateView):
    model = core_models.Workspace
    fields = ["name", "is_default",]
    template_name = "demo/generic/create.html"

    def get_success_url(self):
        return reverse_lazy("demo:workspace-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        demo_utils.update_context_main(self.request, context)
        return context

    def form_valid(self, form):
        if not form.instance.pk:
            form.instance.created_by = self.request.user
        form.instance.updated_by = self.request.user
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(created_by=self.request.user)
        )
        if cnd:
            msg = "Name(lowercased) should be unique for a user."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class WorkspaceUpdateView(LoginRequiredMixin, djev.UpdateView):
    model = core_models.Workspace
    fields = ["name", "is_default",]
    template_name = "demo/generic/update.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:workspace-detail", kwargs={"pk": self.object.pk})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        demo_utils.update_context_main(self.request, context)
        return context

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(created_by=self.request.user)
            & ~Q(pk=self.object.pk)
        )
        if cnd:
            msg = "Name(lowercased) should be unique for a user."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class WorkspaceDeleteView(LoginRequiredMixin, djev.DeleteView):
    model = core_models.Workspace
    success_url = reverse_lazy("demo:home")
    template_name = "demo/generic/delete.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        demo_utils.update_context_main(self.request, context)
        return context


class CategoryCreateView(LoginRequiredMixin, demo_utils.CustomWsCreateView):
    model = core_models.Category
    template_name = "demo/generic/create.html"
    fields = ["name", "description", "workspace", "parent"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
            & Q(parent=form.instance.parent)
        )
        if cnd:
            msg = "Name(lowercased)-workspace-parent should be unique."
            form.add_error("name",
                           ValidationError(message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class CategoryUpdateView(LoginRequiredMixin, demo_utils.CustomWsUpdateView):
    model = core_models.Category
    template_name = "demo/generic/update.html"
    fields = ["name", "description", "workspace", "parent"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
            & ~Q(pk=self.object.pk)
        )
        if cnd:
            msg = "Name(lowercased)-workspace-parent should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class CategoryDeleteView(LoginRequiredMixin, demo_utils.CustomWsDeleteView):
    model = core_models.Category
    template_name = "demo/generic/delete.html"

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})


class TagCreateView(LoginRequiredMixin, demo_utils.CustomWsCreateView):
    model = core_models.Tag
    template_name = "demo/generic/create.html"
    fields = ["name", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class TagUpdateView(LoginRequiredMixin, demo_utils.CustomWsUpdateView):
    model = core_models.Tag
    template_name = "demo/generic/update.html"
    fields = ["name", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
            & ~Q(pk=self.object.pk)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class TagDeleteView(LoginRequiredMixin, demo_utils.CustomWsDeleteView):
    model = core_models.Tag
    template_name = "demo/generic/delete.html"

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})


class PriorityCreateView(LoginRequiredMixin, demo_utils.CustomWsCreateView):
    model = core_models.Priority
    template_name = "demo/generic/create.html"
    fields = ["name", "order", "description", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class PriorityUpdateView(LoginRequiredMixin, demo_utils.CustomWsUpdateView):
    model = core_models.Priority
    template_name = "demo/generic/update.html"
    fields = ["name", "order", "description", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
            & ~Q(pk=self.object.pk)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class PriorityDeleteView(LoginRequiredMixin, demo_utils.CustomWsDeleteView):
    model = core_models.Priority
    template_name = "demo/generic/delete.html"

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})


class StatusCreateView(LoginRequiredMixin, demo_utils.CustomWsCreateView):
    model = core_models.Status
    template_name = "demo/generic/create.html"
    fields = ["name", "order", "description", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class StatusUpdateView(LoginRequiredMixin, demo_utils.CustomWsUpdateView):
    model = core_models.Status
    template_name = "demo/generic/update.html"
    fields = ["name", "order", "description", "workspace"]

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        cnd = self.model.objects.filter(
            Q(name__iexact=form.instance.name)
            & Q(workspace=form.instance.workspace)
            & ~Q(pk=self.object.pk)
        )
        if cnd:
            msg = "Name(lowercased)-workspace should be unique."
            form.add_error("name", ValidationError(
                message=msg, code='invalid'))
            return super().form_invalid(form)
        return super().form_valid(form)


class StatusDeleteView(LoginRequiredMixin, demo_utils.CustomWsDeleteView):
    model = core_models.Status
    template_name = "demo/generic/delete.html"

    def get_success_url(self):
        return reverse_lazy("demo:workspace-manage", kwargs={"pk": self.object.workspace.pk})


class WorkspaceCommentUpdateView(LoginRequiredMixin, djev.UpdateView):
    model = core_models.WorkspaceComment
    template_name = "demo/generic/update.html"
    fields = ["content", "workspace", "parent"]

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:workspace-detail", kwargs={
            "pk": self.object.workspace.pk
        })

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.workspace.name
        demo_utils.update_context_main(
            self.request, context, ws_name)
        return context


class WorkspaceCommentDeleteView(LoginRequiredMixin, djev.DeleteView):
    model = core_models.WorkspaceComment
    template_name = "demo/generic/delete.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:workspace-detail", kwargs={
            "pk": self.object.workspace.pk
        })

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.workspace.name
        demo_utils.update_context_main(
            self.request, context, ws_name)
        return context


class CategoryCommentUpdateView(LoginRequiredMixin, djev.UpdateView):
    model = core_models.CategoryComment
    template_name = "demo/generic/update.html"
    fields = ["content", "category", "parent"]

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:category-detail", kwargs={
            "pk": self.object.category.pk
        })

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.category.workspace.name
        cat_name = self.object.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context


class CategoryCommentDeleteView(LoginRequiredMixin, djev.DeleteView):
    model = core_models.CategoryComment
    template_name = "demo/generic/delete.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:category-detail", kwargs={
            "pk": self.object.category.pk
        })

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.category.workspace.name
        cat_name = self.object.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context


@login_required(login_url='accounts/login/')
def home(request):
    template = "demo/index.html"
    context = {
        "home_active": True,
    }
    demo_utils.update_context_main(request, context)
    return render(request, template, context)


@login_required
def workspace_manage(request, pk):
    template = "demo/workspace/manage.html"
    context = {}
    workspace = core_models.Workspace.objects.get(pk=pk)
    if request.user != workspace.created_by:
        raise PermissionDenied("You are not the creator of this object.")
    demo_utils.update_context_main(request, context, workspace.name)
    return render(request, template, context)


@login_required
def workspace_detail(request, pk):
    template = "demo/workspace/detail.html"
    context = {}
    workspace = core_models.Workspace.objects.get(pk=pk)
    if request.user != workspace.created_by:
        raise PermissionDenied("You are not the creator of this object.")
    demo_utils.update_context_main(request, context, workspace.name)

    comments = workspace.comments.all()
    comments_tree = core_models.WorkspaceComment.get_tree(comments)
    rendered_comments = core_models.WorkspaceComment.render_comments_tree(
        comments_tree)
    if request.method == "POST":
        comment_form = demo_forms.WorkspaceCommentForm(
            request.POST, request.FILES, prefix="comment")
        comment_form.fields["workspace"].queryset = core_models.Workspace.objects\
            .filter(pk=workspace.pk)
        comment_form.fields["parent"].queryset = core_models\
            .WorkspaceComment.objects.filter(workspace=workspace)
        if comment_form.is_valid() and comment_form.has_changed():
            comment_form.instance.created_by = request.user
            comment_form.save()
            return HttpResponseRedirect(request.path)
    else:
        comment_form = demo_forms.WorkspaceCommentForm(prefix="comment", initial={
            "workspace": workspace,
        })
        comment_form.fields["workspace"].queryset = core_models.Workspace.objects.filter(
            pk=workspace.pk)
        comment_form.fields["parent"].queryset = core_models.WorkspaceComment.objects.filter(
            workspace=workspace)

    context.update({
        "workspace": workspace,
        "comments": comments,
        "rendered_comments": rendered_comments,
        "comment_form": comment_form,
    })
    return render(request, template, context)


@login_required
def category_detail(request, cat_pk):
    template = "demo/category.html"
    context = {}
    cat_name = core_models.Category.objects.get(pk=cat_pk).name
    category = core_models.Category.objects.get(pk=cat_pk)
    ws_pk = category.workspace.pk
    ws_name = core_models.Workspace.objects.get(pk=ws_pk).name
    if request.user != category.created_by:
        raise PermissionDenied("You are not the creator of this object.")
    demo_utils.update_context_main(request, context, ws_name, cat_name)

    comments = category.comments.all()
    comments_tree = core_models.CategoryComment.get_tree(comments)
    rendered_comments = core_models.CategoryComment.render_comments_tree(
        comments_tree)
    if request.method == "POST":
        comment_form = demo_forms.CategoryCommentForm(
            request.POST, request.FILES, prefix="comment")
        comment_form.fields["category"].queryset = core_models.Category.objects\
            .filter(pk=category.pk)
        comment_form.fields["parent"].queryset = core_models\
            .CategoryComment.objects.filter(category=category)
        if comment_form.is_valid() and comment_form.has_changed():
            comment_form.instance.created_by = request.user
            comment_form.save()
            return HttpResponseRedirect(request.path)
    else:
        comment_form = demo_forms.CategoryCommentForm(prefix="comment", initial={
            "category": category,
        })
        comment_form.fields["category"].queryset = core_models.Category.objects.filter(
            pk=category.pk)
        comment_form.fields["parent"].queryset = core_models.CategoryComment.objects.filter(
            category=category)

    context.update({
        "category": category,
        "comments": comments,
        "rendered_comments": rendered_comments,
        "comment_form": comment_form,
    })

    return render(request, template, context)


@login_required
def task_detail_view(request, uuid):
    template = "demo/task/detail.html"
    context = {}
    task = core_models.Task.objects.get(uuid=uuid)
    if request.user != task.created_by:
        raise PermissionDenied("You are not the creator of this object.")
    ws_pk = task.workspace.pk
    cat_pk = task.category.pk
    demo_utils.update_context_main(request, context, task.workspace.name,
                                   task.category.name)
    comments = task.comments.all()
    comments_tree = core_models.TaskComment.get_tree(comments)
    rendered_comments = core_models.TaskComment.render_comments_tree(
        comments_tree)
    task_queryset = core_models.Task.objects.filter(uuid=uuid)
    if request.method == "POST":
        task_form = demo_forms.TaskForm(
            request.POST, request.FILES, instance=task, prefix="task")
        comment_form = demo_forms.TaskCommentForm(
            request.POST, request.FILES, prefix="comment")
        comment_form.fields["task"].queryset = core_models.Task.objects\
            .filter(pk=task.pk)
        comment_form.fields["parent"].queryset = core_models\
            .TaskComment.objects.filter(task=task)
        if comment_form.is_valid() and comment_form.has_changed():
            comment_form.instance.created_by = request.user
            comment_form.save()
            return HttpResponseRedirect(request.path)
        if task_form.is_valid():
            task_form.save()
            return HttpResponseRedirect(request.path)
    else:
        task_form = demo_forms.TaskForm(instance=task, prefix="task")
        comment_form = demo_forms.TaskCommentForm(prefix="comment", initial={
            "task": task,
        })
        comment_form.fields["task"].queryset = core_models.Task.objects.filter(
            pk=task.pk)
        comment_form.fields["parent"].queryset = core_models.TaskComment.objects.filter(
            task=task)

    context.update({
        "task": task,
        "children": task.get_children(task),
        "rendered_task_hierarchy": task.render_hierarchy("title"),
        "comments": comments,
        "rendered_comments": rendered_comments,
        "task_form": task_form,
        "comment_form": comment_form,
    })
    return render(request, template, context)


class TaskCreateView(LoginRequiredMixin, demo_utils.CustomCreateView):
    model = core_models.Task
    template_name = "demo/task/create.html"
    form_class = demo_forms.TaskForm

    def get_form_class(self):
        model_form = super().get_form_class()
        ws_pk, cat_pk = self.get_details()
        model_form.base_fields["workspace"].queryset \
            = core_models.Workspace.objects.filter(pk=ws_pk)
        model_form.base_fields["category"].queryset \
            = core_models.Category.objects.filter(pk=cat_pk)
        model_form.base_fields["project"].queryset \
            = core_models.Project.objects.filter(workspace__pk=ws_pk,
                                                 category__pk=cat_pk)
        model_form.base_fields["parent"].queryset \
            = core_models.Task.objects.filter(workspace__pk=ws_pk,
                                              category__pk=cat_pk)
        model_form.base_fields["status"].queryset \
            = core_models.Status.objects.filter(workspace__pk=ws_pk)
        model_form.base_fields["priority"].queryset \
            = core_models.Priority.objects.filter(workspace__pk=ws_pk)
        return model_form

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "task_form": context["form"],
        })
        context.pop("form")
        return context


class TaskDeleteView(LoginRequiredMixin, demo_utils.CustomDeleteView):
    model = core_models.Task
    template_name = "demo/generic/delete.html"


class TaskCommentUpdateView(LoginRequiredMixin, djev.UpdateView):
    model = core_models.TaskComment
    template_name = "demo/generic/update.html"
    fields = ["content", "task", "parent"]

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.updated_by = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy("demo:task-detail", kwargs={"uuid": self.object.task.uuid})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.task.workspace.name
        cat_name = self.object.task.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context


class TaskCommentDeleteView(LoginRequiredMixin, djev.DeleteView):
    model = core_models.TaskComment
    template_name = "demo/generic/delete.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:task-detail", kwargs={"uuid": self.object.task.uuid})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.task.workspace.name
        cat_name = self.object.task.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context


@login_required
def project_detail_view(request, uuid):
    template = "demo/project/detail.html"
    context = {}
    project = core_models.Project.objects.get(uuid=uuid)
    if request.user != project.created_by:
        raise PermissionDenied("You are not the creator of this object.")
    demo_utils.update_context_main(request, context, project.workspace.name,
                                   project.category.name)
    comments = project.comments.all()
    comments_tree = core_models.ProjectComment.get_tree(comments)
    rendered_comments = core_models.ProjectComment.render_comments_tree(
        comments_tree)
    tasks = project.tasks.all()
    tasks_tree = core_models.Task.get_tree(tasks)
    rendered_tasks = core_models.Task.render_tree(tasks_tree, "title")
    project_queryset = core_models.Project.objects.filter(uuid=uuid)
    if request.method == "POST":
        project_form = demo_forms.ProjectForm(
            request.POST, request.FILES, instance=project, prefix="project")
        comment_form = demo_forms.ProjectCommentForm(
            request.POST, request.FILES, prefix="comment")
        comment_form.fields["project"].queryset = core_models.Project.objects\
            .filter(pk=project.pk)
        comment_form.fields["parent"].queryset = core_models\
            .ProjectComment.objects.filter(project=project)
        if comment_form.is_valid() and comment_form.has_changed():
            comment_form.instance.created_by = request.user
            comment_form.save()
            return HttpResponseRedirect(request.path)
        if project_form.is_valid():
            project_form.save()
            return HttpResponseRedirect(request.path)
    else:
        project_form = demo_forms.ProjectForm(
            instance=project, prefix="project")
        comment_form = demo_forms.ProjectCommentForm(
            prefix="comment",
            initial={
                "project": project,
            })
        comment_form.fields["project"].queryset = core_models.Project.objects.filter(
            pk=project.pk)
        comment_form.fields["parent"].queryset = core_models.ProjectComment.objects.filter(
            project=project)
    context.update({
        "project": project,
        "children": project.get_children(project),
        "rendered_project_hierarchy": project.render_hierarchy("title"),
        "tasks": tasks,
        "rendered_tasks": rendered_tasks,
        "comments": comments,
        "rendered_comments": rendered_comments,
        "project_form": project_form,
        "comment_form": comment_form,
    })
    return render(request, template, context)


class ProjectCreateView(LoginRequiredMixin, demo_utils.CustomCreateView):
    model = core_models.Project
    template_name = "demo/project/create.html"
    form_class = demo_forms.ProjectForm

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context.update({
            "project_form": context["form"]
        })
        context.pop("form")
        return context


class ProjectDeleteView(LoginRequiredMixin, demo_utils.CustomDeleteView):
    model = core_models.Project
    template_name = "demo/generic/delete.html"


class ProjectCommentUpdateView(LoginRequiredMixin, djev.UpdateView):
    model = core_models.ProjectComment
    template_name = "demo/generic/update.html"
    fields = ["content", "project", "parent"]

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:project-detail", kwargs={"uuid": self.object.project.uuid})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.project.workspace.name
        cat_name = self.object.project.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context


class ProjectCommentDeleteView(LoginRequiredMixin, djev.DeleteView):
    model = core_models.ProjectComment
    template_name = "demo/generic/delete.html"

    def get(self, request, *args, **kwargs):
        if request.user != self.get_object().created_by:
            raise PermissionDenied("You are not the creator of this object.")
        return super().get(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("demo:project-detail", kwargs={"uuid": self.object.project.uuid})

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        ws_name = self.object.project.workspace.name
        cat_name = self.object.project.category.name
        demo_utils.update_context_main(
            self.request, context, ws_name, cat_name)
        return context

@login_required
def archive_view(request):
    template = "demo/archive.html"
    context = {
        "archive_active": "active",
    }
    demo_utils.update_context_archive(request, context)
    return render(request, template, context)
