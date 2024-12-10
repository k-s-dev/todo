from django.db.models import Q
from demo import utils as demo_utils
from core import models as core_models


def update_context_main(request, context, workspace_name=None, category_name=None):
    """
    Get workspaces and categories from a request object for an user.
    """
    user = request.user
    workspaces = user.workspaces.all()
    workspaces_rendered = demo_utils.render_workspaces(
        workspaces, workspace_name, category_name)
    context.update({
        "workspaces": workspaces,
        "workspaces_rendered": workspaces_rendered,
    })
    if workspace_name:
        workspace = user.workspaces.get(name=workspace_name)
        categories = workspace.categories.all()
        tags = workspace.tags.all()
        priorities = workspace.priorities.all()
        statuses = workspace.statuses.all()
        ws_category_tree = core_models.Category.get_tree(categories)
        ws_categories_detail_rendered = demo_utils.\
            render_category_tree_detailed(ws_category_tree)
        ws_tags_rendered = demo_utils.render_objs(tags, "tag")
        ws_priorities_rendered = demo_utils.render_objs(priorities, "priority")
        ws_statuses_rendered = demo_utils.render_objs(statuses, "status")
        ws_projects = workspace.projects.filter(is_visible=True)
        ws_project_tasks = workspace.tasks.filter(
            project__isnull=False, is_visible=True
        )
        ws_independent_tasks = workspace.tasks.filter(
            project__isnull=True, is_visible=True
        )
        context.update({
            "workspace": workspace,
            "categories": categories,
            "ws_categories_detail_rendered": ws_categories_detail_rendered,
            "ws_tags_rendered": ws_tags_rendered,
            "ws_priorities_rendered": ws_priorities_rendered,
            "ws_statuses_rendered": ws_statuses_rendered,
            "ws_projects": ws_projects,
            "ws_project_tasks": ws_project_tasks,
            "ws_independent_tasks": ws_independent_tasks,
        })
    if category_name:
        category = core_models.Category.objects.get(name=category_name)
        category_projects = category.projects.filter(is_visible=True)
        category_project_tasks = category.tasks.filter(
            project__isnull=False, is_visible=True
        )
        category_independent_tasks = category.tasks.filter(
            project__isnull=True, is_visible=True
        )
        context.update({
            "category": category,
            "category_projects": category_projects,
            "category_project_tasks": category_project_tasks,
            "category_independent_tasks": category_independent_tasks,
        })

def update_context_archive(request, context):
    """
    Update context to include archived projects and tasks.
    """
    user = request.user
    workspaces = user.workspaces.all()
    workspaces_rendered = demo_utils.render_workspaces(workspaces)
    projects = core_models.Project.objects.filter(
        created_by=user, is_visible=False)
    project_tasks = core_models.Task.objects.filter(
        created_by=user, project__isnull=False, is_visible=False)
    independent_tasks = core_models.Task.objects.filter(
        created_by=user, project__isnull=True, is_visible=False)
    context.update({
        "workspaces": workspaces,
        "workspaces_rendered": workspaces_rendered,
        "projects": projects,
        "project_tasks": project_tasks,
        "independent_tasks": independent_tasks,
    })
