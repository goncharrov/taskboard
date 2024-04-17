from django.urls import path
from task import views

urlpatterns = [
    path('', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    ### - Задачи
    path('tasks/',    views.get_tasks, name='tasks'),
    path('tasks/add/', views.add_new_task, name='add_task'),
    path('tasks/<int:pk>/main/', views.get_task_main, name='view_task_main'),
    path('tasks/<int:pk>/chat/', views.get_task_chat, name='view_task_chat'),
    ### - Проекты
    path('projects/', views.GetProjects.as_view(), name='projects'),
    path('projects/add/', views.AddNewProject.as_view(), name='add_project'),
    path('projects/<int:pk>/main/', views.get_project_main, name='view_project_main'),
    path('projects/<int:pk>/tasks/', views.GetProjectTasks.as_view(), name='view_project_tasks'),
]