from .render_category_tree import render_category_tree
from core import models as core_models


def render_workspaces(workspaces, workspace_name=None, category_name=None):
    if workspaces:
        result = '<ul>'
        for workspace in workspaces:
            categories = workspace.categories.all()
            if workspace_name and workspace.name == workspace_name:
                result += f'''
                <li>
                <a href="{workspace.get_absolute_url()}" 
                  class="text-warning-emphasis bg-warning-subtle"
                >Workspace: {workspace.name}</a>
                '''
                result += render_category_tree(
                    core_models.Category.get_tree(categories), category_name)
                result += '</li>'
            else:
                result += f'''
                <li>
                <a href="{workspace.get_absolute_url()}" class="link-secondary"
                    >Workspace: {workspace.name}</a>
                '''
                result += render_category_tree(
                    core_models.Category.get_tree(categories), category_name)
                result += '</li>'
        result += '</ul>'
    else:
        result = ""
    return result
