from django.urls import path
from .views import *

urlpatterns = [
    path('', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
    ### - Задачи
    path('tasks/',    get_tasks, name='tasks'),
    path('tasks/add/', add_new_task, name='add_task'),
    path('tasks/<int:pk>/main/', get_task_main, name='view_task_main'),
    path('tasks/<int:pk>/chat/', get_task_chat_def, name='view_task_chat'),
    ### - Проекты
    path('projects/', get_projects.as_view(), name='projects'),
    path('projects/add/', add_new_project.as_view(), name='add_project'),
    path('projects/<int:pk>/main/', get_project_main, name='view_project_main'),
    path('projects/<int:pk>/tasks/', get_project_tasks.as_view(), name='view_project_tasks'),
]