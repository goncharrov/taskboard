from django.core.management.base import BaseCommand
from task.models import TaskStatus, ProjectStatus, UserRoles


TASK_STATUSES: dict = {
    '1': 'Новая',
    '2': 'В работе', 
    '3': 'Выполнена', 
    '4': 'В ожидании', 
    '5': 'Отменена'
    }

PROJECT_STATUSES: dict = {
    '1': 'В работе', 
    '2': 'Закрыт' 
    }

USER_ROLES: dict = {
    '1': 'Полные права', 
    '2': 'Пользователь'
}

class Command(BaseCommand):
    help = 'Add default task statuses'

    def handle(self, *args, **options) -> str | None:

        for key, value in TASK_STATUSES.items():
            task_status_object = TaskStatus.objects.filter(pk=key).first()
            if task_status_object is None:
                TaskStatus.objects.create(pk=key, title=value)
            else:
                task_status_object.title = value
                task_status_object.save()

        for key, value in PROJECT_STATUSES.items():
            project_status_object = ProjectStatus.objects.filter(pk=key).first()
            if project_status_object is None:
                ProjectStatus.objects.create(pk=key, title=value)
            else:
                project_status_object.title = value
                project_status_object.save()

        for key, value in USER_ROLES.items():
            user_roles_object = UserRoles.objects.filter(pk=key).first()
            if user_roles_object is None:
                UserRoles.objects.create(pk=key, title=value)
            else:
                user_roles_object.title = value
                user_roles_object.save()

        print('All default data created!')
