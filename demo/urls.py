from django.urls import path, include

from demo import views

app_name = "demo"

urlpatterns = [
    path('', views.home, name='home'),

    path('workspace/add/', views.WorkspaceCreateView.as_view(),
         name='workspace-create'),
    path('workspace/<int:pk>/manage/',
         views.workspace_manage, name='workspace-manage'),
    path('workspace/<int:pk>/detail/',
         views.workspace_detail, name='workspace-detail'),
    path('workspace/<int:pk>/update/',
         views.WorkspaceUpdateView.as_view(), name='workspace-update'),
    path('workspace/<int:pk>/delete/',
         views.WorkspaceDeleteView.as_view(), name='workspace-delete'),

    path('workspace/comment/<int:pk>/update/',
         views.WorkspaceCommentUpdateView.as_view(), name='workspace-comment-update'),
    path('workspace/comment/<int:pk>/delete/',
         views.WorkspaceCommentDeleteView.as_view(), name='workspace-comment-delete'),

    path('category/add/',
         views.CategoryCreateView.as_view(),
         name='category-create'),
    path('category/<int:cat_pk>/detail/',
         views.category_detail,
         name='category-detail'),
    path('category/<int:pk>/update/',
         views.CategoryUpdateView.as_view(),
         name='category-update'),
    path('category/<int:pk>/delete/',
         views.CategoryDeleteView.as_view(),
         name='category-delete'),

    path('category/comment/<int:pk>/update/',
         views.CategoryCommentUpdateView.as_view(),
         name='category-comment-update'),
    path('workspace/comment/<int:pk>/delete/',
         views.CategoryCommentDeleteView.as_view(),
         name='category-comment-delete'),

    path('tag/add/', views.TagCreateView.as_view(),
         name='tag-create'),
    path('tag/<int:pk>/update/',
         views.TagUpdateView.as_view(), name='tag-update'),
    path('tag/<int:pk>/delete/',
         views.TagDeleteView.as_view(), name='tag-delete'),

    path('priority/add/', views.PriorityCreateView.as_view(),
         name='priority-create'),
    path('priority/<int:pk>/update/',
         views.PriorityUpdateView.as_view(), name='priority-update'),
    path('priority/<int:pk>/delete/',
         views.PriorityDeleteView.as_view(), name='priority-delete'),

    path('status/add/', views.StatusCreateView.as_view(),
         name='status-create'),
    path('status/<int:pk>/update/',
         views.StatusUpdateView.as_view(), name='status-update'),
    path('status/<int:pk>/delete/',
         views.StatusDeleteView.as_view(), name='status-delete'),

    path('task/add/', views.TaskCreateView.as_view(), name='task-create'),
    path('task/<slug:uuid>/detail/', views.task_detail_view, name='task-detail'),
    path('task/<slug:uuid>/delete/',
         views.TaskDeleteView.as_view(), name='task-delete'),

    path('task/comment/<int:pk>/update/',
         views.TaskCommentUpdateView.as_view(), name='task-comment-update'),
    path('task/comment/<int:pk>/delete/',
         views.TaskCommentDeleteView.as_view(), name='task-comment-delete'),

    path('project/add/', views.ProjectCreateView.as_view(), name='project-create'),
    path('project/<slug:uuid>/detail/',
         views.project_detail_view, name='project-detail'),
    path('project/<slug:uuid>/delete/',
         views.ProjectDeleteView.as_view(), name='project-delete'),

    path('project/comment/<int:pk>/update/',
         views.ProjectCommentUpdateView.as_view(), name='project-comment-update'),
    path('project/comment/<int:pk>/delete/',
         views.ProjectCommentDeleteView.as_view(), name='project-comment-delete'),

    path('archive/', views.archive_view, name='archive'),

    path('signup/', views.SignUpView.as_view(), name='signup'),
]
