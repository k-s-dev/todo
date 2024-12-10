from django.urls import reverse

def render_objs(objs, url_name=None):
    result = f'''
        <table class="table table-striped">
          <thead>
            <tr>
              <th scope="col">#</th>
              <th scope="col">Name</th>
              <th scope="col">Update</th>
              <th scope="col">Delete</th>
            </tr>
          </thead>
          <tbody>
    '''
    for obj in objs:
        url_update = reverse(f"demo:{url_name}-update", kwargs={"pk": obj.pk})\
            + f'?ws_pk={obj.workspace.pk}'
        url_delete = reverse(f"demo:{url_name}-delete", kwargs={"pk": obj.pk})\
            + f'?ws_pk={obj.workspace.pk}'
        result += fr'''
            <tr>
              <th scope="row">{obj.pk}</th>
              <td>{obj.name}</td>
              <td><a href="{url_update}" class="link-primary">Update</a></td>
              <td><a href="{url_delete}" class="link-danger">Delete</a></td>
            </tr>
        '''
    result += f'''
          </tbody>
        </table>
    '''
    return result

