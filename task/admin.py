from django.contrib import admin
from .models import *

class User_Roles_Admin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

class User_Rights_Admin(admin.ModelAdmin):
    list_display = ('id', 'user', 'role')
    list_display_links = ('id', 'user')
    list_filter = ('role',)
    fields = ('user', 'role')

class WorkspaceAdmin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'workspace')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    list_filter = ('workspace',)

class Workspace_Members_Admin(admin.ModelAdmin):
    list_display = ('id', 'workspace', 'user')
    list_display_links = ('id', 'user')
    search_fields = ('workspace', 'user')
    list_filter = ('workspace','user')
    fields = ('workspace', 'user')

class Project_Status_Admin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'workspace','owner', 'created_at', 'status', 'department')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    list_filter = ('workspace', 'owner', 'department')
    fields = ('title', 'description', 'workspace', 'department', 'owner', 'status', 'finish_date', 'clousing_date')

class Project_Members_Admin(admin.ModelAdmin):
    list_display = ('id', 'user', 'project')
    list_display_links = ('id', 'user')
    list_filter = ('project',)
    fields = ('project', 'user')

class Task_Status_Admin(admin.ModelAdmin):
    list_display = ('id', 'title')
    list_display_links = ('id', 'title')
    search_fields = ('title',)

class TaskAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'workspace', 'department', 'owner', 'created_at', 'status')
    list_display_links = ('id', 'title')
    search_fields = ('title',)
    list_filter = ('workspace', 'department', 'project', 'owner', 'executor', 'status')
    readonly_fields = ('created_at',)
    fields = ('title', 'description', 'workspace', 'department', 'project', 'owner', 'executor', 'status', 'created_at', 'finish_date', 'clousing_date')

class Task_Members_Admin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user')
    list_display_links = ('id', 'task')
    list_filter = ('task', 'user')

class Task_Finish_Date_History_Admin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user')
    list_display_links = ('id', 'task')
    list_filter = ('task', 'user')

class Task_Dispute_Admin(admin.ModelAdmin):
    list_display = ('id', 'task', 'user', 'in_reply_task_dispute', 'in_reply_user', 'content', 'file', 'created_at')
    list_display_links = ('id', 'task')
    list_filter = ('task', 'user')

class Task_New_Messages_Admin(admin.ModelAdmin):
    list_display = ('task', 'user', 'new_messages')
    list_display_links = ('task',)
    list_filter = ('task', 'user')

class Unauthorized_Access_Attempts_Admin(admin.ModelAdmin):
    list_display = ('event_date', 'user', 'url')
    list_display_links = ('event_date',)
    list_filter = ('user',)

admin.site.register(User_Roles, User_Roles_Admin)
admin.site.register(User_Rights, User_Rights_Admin)
admin.site.register(Workspace, WorkspaceAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(Workspace_Members, Workspace_Members_Admin)
admin.site.register(Project_Status, Project_Status_Admin)
admin.site.register(Project, ProjectAdmin)
admin.site.register(Project_Members, Project_Members_Admin)
admin.site.register(Task_Status, Task_Status_Admin)
admin.site.register(Task, TaskAdmin)
admin.site.register(Task_Members, Task_Members_Admin)
admin.site.register(Task_Finish_Date_History, Task_Finish_Date_History_Admin)
admin.site.register(Task_Dispute, Task_Dispute_Admin)
admin.site.register(Task_New_Messages, Task_New_Messages_Admin)
admin.site.register(Unauthorized_Access_Attempts, Unauthorized_Access_Attempts_Admin)

