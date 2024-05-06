from django.contrib import admin
from task import models


@admin.register(models.UserRoles)
class UserRolesAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)


@admin.register(models.UserRights)
class UserRightsAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'user', 'role')
    list_display_links: tuple = ('id', 'user')
    list_filter: tuple = ('role',)
    fields: tuple = ('user', 'role')

@admin.register(models.Workspace)
class WorkspaceAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)

@admin.register(models.Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title', 'workspace')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)
    list_filter: tuple = ('workspace',)

@admin.register(models.WorkspaceMembers)
class WorkspaceMembersAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'workspace', 'user')
    list_display_links: tuple = ('id', 'user')
    search_fields: tuple = ('workspace', 'user')
    list_filter: tuple = ('workspace','user')
    fields: tuple = ('workspace', 'user')

@admin.register(models.ProjectStatus)
class ProjectStatusAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)

@admin.register(models.Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title', 'workspace','owner', 'created_at', 'status', 'department')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)
    list_filter: tuple = ('workspace', 'owner', 'department')
    fields: tuple = ('title', 'description', 'workspace', 'department', 'owner', 'status', 'finish_date', 'clousing_date')

@admin.register(models.ProjectMembers)
class ProjectMembersAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'user', 'project')
    list_display_links: tuple = ('id', 'user')
    list_filter: tuple = ('project',)
    fields: tuple = ('project', 'user')

@admin.register(models.TaskStatus)
class TaskStatusAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)

@admin.register(models.Task)
class TaskAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'title', 'workspace', 'department', 'owner', 'created_at', 'status')
    list_display_links: tuple = ('id', 'title')
    search_fields: tuple = ('title',)
    list_filter: tuple = ('workspace', 'department', 'project', 'owner', 'executor', 'status')
    readonly_fields: tuple = ('created_at',)
    fields: tuple = ('title', 'description', 'workspace', 'department', 'project', 'owner', 'executor', 'status', 'created_at', 'finish_date', 'clousing_date')

@admin.register(models.TaskMembers)
class TaskMembersAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'task', 'user')
    list_display_links: tuple = ('id', 'task')
    list_filter: tuple = ('task', 'user')

@admin.register(models.TaskFinishDateHistory)
class TaskFinishDateHistoryAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'task', 'user')
    list_display_links: tuple = ('id', 'task')
    list_filter: tuple = ('task', 'user')

@admin.register(models.TaskDispute)
class TaskDisputeAdmin(admin.ModelAdmin):
    list_display: tuple = ('id', 'task', 'user', 'in_reply_task_dispute', 'in_reply_user', 'content', 'file', 'created_at')
    list_display_links: tuple = ('id', 'task')
    list_filter: tuple = ('task', 'user')

@admin.register(models.TaskNewMessages)
class TaskNewMessagesAdmin(admin.ModelAdmin):
    list_display: tuple = ('task', 'user', 'new_messages')
    list_display_links: tuple = ('task',)
    list_filter: tuple = ('task', 'user')

@admin.register(models.UnauthorizedAccessAttempts)
class UnauthorizedAccessAttemptsAdmin(admin.ModelAdmin):
    list_display: tuple = ('event_date', 'user', 'url')
    list_display_links: tuple = ('event_date',)
    list_filter: tuple = ('user',)
