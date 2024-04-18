# import datetime
import locale
from django.contrib.auth.models import User
from django.db import models
from django.urls import reverse
from ckeditor_uploader.fields import RichTextUploadingField

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')

# from django.contrib.auth import get_user_model
# User = get_user_model()

NAME_OF_USER_RIGHTS_FULL = 'Полные права'


def get_name(self):
    return f'{self.last_name} {self.first_name}'

User.add_to_class("__str__", get_name)

# Profile Details - Company, Job title, Department
# user_settings ???


class User_Roles(models.Model):
    title = models.CharField(max_length=50, verbose_name='Наименование')

    @property
    def is_full(self):
        return self.title == NAME_OF_USER_RIGHTS_FULL

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Роль пользователя'
        verbose_name_plural = 'Роли пользователей'
        ordering = ['title',]

class User_Rights(models.Model):
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь',
                             related_name='related_right')
    role = models.ForeignKey(User_Roles, on_delete=models.PROTECT, verbose_name='Роль',
                             related_name='related_right')

    def __str__(self):
        return self.role.title

    class Meta:
        verbose_name = 'Права пользователя'
        verbose_name_plural = 'Права пользователей'
        ordering = ['user', 'role']

class Workspace(models.Model):
    title = models.CharField(max_length=100, verbose_name='Наименование')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Рабочее пространство'
        verbose_name_plural = 'Рабочие пространства'
        ordering = ['title']

class Department(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, verbose_name='Рабочее пространство', related_name='related_department')

    def __str__(self):
        return f'{self.workspace.title} : {self.title}'

    class Meta:
        verbose_name = 'Подразделение'
        verbose_name_plural = 'Подразделения'
        ordering = ['workspace','title']

class Workspace_Members(models.Model):
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, verbose_name='Проект',
                                  related_name='related_workspace_members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Участник',
                             related_name='related_workspace_members')

    def __str__(self):
        return f'{self.workspace.title} : {self.user.username}'

    class Meta:
        verbose_name = 'Участник пространства'
        verbose_name_plural = 'Участники пространства'
        ordering = ['workspace','user']

class Project_Status(models.Model):
    title = models.CharField(max_length=50, verbose_name='Наименование')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статус проекта'
        verbose_name_plural = 'Статусы проекта'
        ordering = ['title']

class Project(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование')
    # description = models.TextField(blank=True, verbose_name='Описание')
    description = RichTextUploadingField(blank=True, null=True, verbose_name='Описание')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, verbose_name='Рабочее пространство',
                                  related_name='related_project')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Подразделение',
                                   related_name='related_project')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец',
                              related_name='related_project')
    status = models.ForeignKey(Project_Status, on_delete=models.PROTECT, verbose_name='Состояние',
                               related_name='related_project')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    finish_date = models.DateField(blank=True, null=True, verbose_name='Плановая дата выполнения')
    clousing_date = models.DateField(blank=True, null=True, verbose_name='Дата закрытия')


    def __str__(self):
        return self.title

    def get_absolute_url_main(self):
        return reverse('view_project_main', kwargs={"pk": self.pk})

    def get_absolute_url_tasks(self):
        return reverse('view_project_tasks', kwargs={"pk": self.pk})

    class Meta:
        verbose_name = 'Проект'
        verbose_name_plural = 'Проекты'
        ordering = ['created_at']

class Project_Members(models.Model):
    project = models.ForeignKey(Project, on_delete=models.PROTECT, verbose_name='Проект',
                                  related_name='related_project_members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Участник',
                             related_name='related_project_members')

    def __str__(self):
        # return f'{self.project.title} : {self.user.username}'
        return self.project.title

    class Meta:
        verbose_name = 'Участник проекта'
        verbose_name_plural = 'Участники проекта'
        ordering = ['project', 'user']

class Task_Status(models.Model):
    title = models.CharField(max_length=50, verbose_name='Наименование')

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Статус задачи'
        verbose_name_plural = 'Статусы задачи'
        ordering = ['id']

class Task(models.Model):
    title = models.CharField(max_length=150, verbose_name='Наименование')
    # description = models.TextField(blank=True, verbose_name='Описание')
    description = RichTextUploadingField(blank=True, null=True, verbose_name='Описание')
    workspace = models.ForeignKey(Workspace, on_delete=models.PROTECT, verbose_name='Рабочее пространство',
                                  related_name='related_task')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Владелец',
                             related_name='related_task_owner')
    executor = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Исполнитель',
                             related_name='related_task_executor')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    finish_date = models.DateField(blank=True, null=True, verbose_name='Плановая дата выполнения')
    status = models.ForeignKey(Task_Status, on_delete=models.PROTECT, verbose_name='Состояние',
                             related_name='related_task')
    project = models.ForeignKey(Project, blank=True, null=True,  on_delete=models.PROTECT, verbose_name='Проект', related_name='related_task')
    department = models.ForeignKey(Department, on_delete=models.PROTECT, verbose_name='Подразделение',
                                   related_name='related_task')
    clousing_date = models.DateField(blank=True, null=True, verbose_name='Дата закрытия')

    def __str__(self):
        return self.title

    def get_absolute_url_main(self):
        return reverse('view_task_main', kwargs={"pk": self.pk})

    def get_absolute_url_chat(self):
        return reverse('view_task_chat', kwargs={"pk": self.pk})

    class Meta:
        verbose_name = 'Задача'
        verbose_name_plural = 'Задачи'
        ordering = ['created_at']

class Task_Members(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name='Задача',
                                  related_name='related_task_members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Участник',
                             related_name='related_task_members')

    def __str__(self):
        return f'{self.task.title} : {self.user.username}'

    class Meta:
        verbose_name = 'Участник задачи'
        verbose_name_plural = 'Участники задачи'
        ordering = ['task', 'user']

class Task_Finish_Date_History(models.Model):
    task = models.ForeignKey(Task, on_delete=models.PROTECT, verbose_name='Задача',
                             related_name='related_task_finish_date_history')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Установил',
                             related_name='related_task_finish_date_history')
    finish_date = models.DateTimeField(verbose_name='Плановая дата выполнения')

    def __str__(self):
        return f'{self.task.title} : {self.user.name} : {self.finish_date}'

    class Meta:
        verbose_name = 'История изменения плановой даты выполнения'
        verbose_name_plural = 'Истории изменения плановых дат выполнения'
        ordering = ['task', 'user', 'finish_date']

class Task_Dispute(models.Model):
    task = models.ForeignKey(Task, related_name='related_task_dispute', on_delete=models.CASCADE, verbose_name='Задача')
    user = models.ForeignKey(User, related_name='related_task_dispute', on_delete=models.CASCADE, verbose_name='Автор')
    in_reply_task_dispute = models.IntegerField(blank=True, default=0, verbose_name='ID родительского сообщения')
    in_reply_user = models.ForeignKey(User, blank=True,  null=True, related_name='related_task_dispute_in_reply_user', on_delete=models.CASCADE)
    content = models.TextField(blank=True, verbose_name='Сообщение')
    file = models.FileField(upload_to='files/%Y/%m/%d/', blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')

    class Meta:
        verbose_name = 'Обсуждение задачи'
        verbose_name_plural = 'Обсуждение задач'
        ordering = ['task', 'user']

class Task_New_Messages(models.Model):
    task = models.ForeignKey(Task, related_name='related_task_message', on_delete=models.CASCADE, verbose_name='Задача')
    user = models.ForeignKey(User, related_name='related_task_message', on_delete=models.CASCADE, verbose_name='Пользователь')
    new_messages = models.IntegerField(default=0, verbose_name='Кол-во новых сообщений')

    class Meta:
        verbose_name = 'Новые сообщения в задаче'
        verbose_name_plural = 'Новые сообщения в задаче'
        ordering = ['task', 'user']

class Unauthorized_Access_Attempts(models.Model):
    url = models.CharField(max_length=150, verbose_name='Url')
    user = models.ForeignKey(User, on_delete=models.PROTECT, verbose_name='Пользователь')
    event_date = models.DateTimeField(auto_now_add=True, verbose_name='Дата события')

    def __str__(self):
        return f'{self.event_date} : {self.user.username} : {self.url}'

    class Meta:
        verbose_name = 'Попытки несанкционированного доступа'
        verbose_name_plural = 'Попытки несанкционированного доступа'
        ordering = ['-event_date',]