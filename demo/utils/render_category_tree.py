from django.urls import reverse

def render_category_tree(tree, category_name=None):
    result = '<ul>'
    for k, v in tree.items():
        if category_name and k.name == category_name:
            result += f'''
            <li>
            <a href="{k.get_absolute_url()}"
              class="text-danger-emphasis bg-danger-subtle"
            >{k.name}</a>
            </li>
            '''
        else:
            result += f'''
            <li>
            <a href="{k.get_absolute_url()}">{k.name}</a>
            </li>
            '''
        if v:
            result += render_category_tree(v, category_name)
    result += '</ul>'
    return result


def render_category_tree_detailed(tree):
    result = '<ul class="list-styled">'
    for k, v in tree.items():
        url_update = reverse("demo:category-update", kwargs={"pk": k.pk})\
            + f'?ws_pk={k.workspace.pk}&cat_pk={k.pk}'
        url_delete = reverse("demo:category-delete", kwargs={"pk": k.pk})\
            + f'?ws_pk={k.workspace.pk}&cat_pk={k.pk}'
        result += f'''
        <li>
            <span class="fs-5">{k.name}: </span>
            <span class="d-inline-block float-end">
            <a href="{url_delete}" class="link-danger">Delete</a>
            </span>
            <span class="d-inline-block me-2 float-end">
            <a href="{url_update}" class="link-primary">Update</a>
            </span>
        </li>
        '''
        if v:
            result += render_category_tree_detailed(v)
    result += '</ul>'
    return result
