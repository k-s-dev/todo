from django.urls import path, include
from rest_framework.routers import DefaultRouter
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from . import views

app_name = 'api'


router = DefaultRouter(use_regex_path=False)
router.register('users', views.UserViewSet, basename='user')
router.register('workspace', views.WorkspaceViewSet, basename='workspace')
router.register('workspace/<int:ws_pk>/comment',
                views.WorkspaceCommentViewSet,
                basename='workspace-comment')
router.register('workspace/<int:ws_pk>/tag',
                views.TagViewSet,
                basename='tag')
router.register('workspace/<int:ws_pk>/priority',
                views.PriorityViewSet,
                basename='priority')
router.register('workspace/<int:ws_pk>/status',
                views.StatusViewSet,
                basename='status')
router.register('workspace/<int:ws_pk>/category',
                views.CategoryViewSet,
                basename='category')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/comment',
                views.CategoryCommentViewSet,
                basename='category-comment')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/project',
                views.ProjectViewSet,
                basename='project')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/project/<int:pr_pk>/comment',
                views.ProjectCommentViewSet,
                basename='project-comment')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/project/<int:pr_pk>/task',
                views.ProjectTaskViewSet,
                basename='project-task')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/task',
                views.TaskViewSet,
                basename='task')
router.register('workspace/<int:ws_pk>/category/<int:cat_pk>/task/<int:task_pk>/comment',
                views.TaskCommentViewSet,
                basename='task-comment')

urlpatterns = [
    path('', include(router.urls)),
    path('schema/', SpectacularAPIView.as_view(), name='schema'),
    path('docs/', SpectacularSwaggerView.as_view(url_name='api:schema'),
         name='docs'),
]
