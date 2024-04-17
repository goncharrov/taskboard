from django.db import connection
from django.db.models.expressions import RawSQL
from django.contrib.auth.models import User
from task.models import Project


# Получим всех пользователей по списку рабочих пространств
def get_users_by_workspace(workspace_list):

    selection_list = []
    for workspace_item in workspace_list:
        selection_list.append(workspace_item)

    request_text = '''
    SELECT 
        users.id
    FROM
        auth_user users,
        task_workspace_members members            
    WHERE
        members.user_id = users.id            
        AND members.workspace_id in (%s)                     
    GROUP by
        users.id        
    '''

    request_text = request_text % ','.join(['%s'] * len(workspace_list))

    users_qs = User.objects.filter(id__in=RawSQL(request_text, selection_list))

    return users_qs.order_by('last_name')

# Получим проекты пользователя
def get_user_projects(current_user_id, filters):

    workspace_id = filters["workspace"] if filters is not None else None
    department_id = filters["department"] if filters is not None else None
    status_id = 1 if filters is not None else None

    request_text = '''

    select 
        all_projects_user.id
    FROM        

    (select 
        projects.id as id   
    FROM 
        task_project projects
    WHERE
        projects.owner_id = %(current_user_id)s
        AND (%(workspace_id)s IS NULL OR projects.workspace_id = %(workspace_id)s)
        AND (%(department_id)s IS NULL OR projects.department_id = %(department_id)s)
        AND (%(status_id)s IS NULL OR projects.status_id = %(status_id)s)                            

    UNION ALL

    select 
        projects.id
    FROM 
        task_project_members project_members,
        task_project projects               
    WHERE
        project_members.project_id = projects.id
        AND project_members.user_id = %(current_user_id)s
        AND (%(workspace_id)s IS NULL OR projects.workspace_id = %(workspace_id)s)
        AND (%(department_id)s IS NULL OR projects.department_id = %(department_id)s)
        AND (%(status_id)s IS NULL OR projects.status_id = %(status_id)s)      
    ) as all_projects_user               

    GROUP by
        all_projects_user.id

    ORDER BY
        all_projects_user.id

    '''

    filters_data: dict = {
        'current_user_id': current_user_id,
        'workspace_id': workspace_id,
        'department_id': department_id,
        'status_id': status_id
    }

    with connection.cursor() as cursor:
        cursor.execute(request_text, filters_data)
        projects_id = [item[0] for item in cursor.fetchall()]
        projects_qs = Project.objects.filter(id__in=projects_id)

        return projects_qs


# Получим список id рабочих пространств
def get_user_workspaces_list(current_user) -> list:

    workspace_list = []
    user_workspaces = current_user.related_workspace_members.all()
    for item_workspace in user_workspaces:
        workspace_list.append(item_workspace.workspace.id)

    return workspace_list
