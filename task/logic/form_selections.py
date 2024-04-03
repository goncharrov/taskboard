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

    # AND auth_user.is_superuser = false

    request_text = request_text % ','.join(['%s'] * len(workspace_list))

    users_qs = User.objects.filter(id__in=RawSQL(request_text, selection_list))

    return users_qs.order_by('last_name')

# Получим проекты пользователя
def get_user_projects(current_user_id, filters):

    workspace_id = filters["workspace"] if filters is not None else ""
    department_id = filters["department"] if filters is not None else ""
    status_id = 1 if filters is not None else ""

    request_text = f"""

    select 
        all_projects_user.id
    FROM        

    (select 
        projects.id as id   
    FROM 
        task_project projects                
    WHERE
        projects.owner_id = %s 
        {'AND projects.workspace_id = %s' if workspace_id != "" else ''}
        {'AND projects.department_id = %s' if department_id != "" else ''}  
        {'AND projects.status_id = %s' if status_id != "" else ''}              

    UNION ALL

    select 
        projects.id
    FROM 
        task_project_members project_members,
        task_project projects               
    WHERE
        project_members.project_id = projects.id                
        AND project_members.user_id = %s
        {'AND projects.workspace_id = %s' if workspace_id != "" else ''}
        {'AND projects.department_id = %s' if department_id != "" else ''}  
        {'AND projects.status_id = %s' if status_id != "" else ''}         
        ) as all_projects_user               

    GROUP by
        all_projects_user.id
    """

    # print(request_text)

    selection_list = []
    # 1 запрос
    selection_list.append(current_user_id)
    if filters is not None:
        selection_list.append(workspace_id)
        selection_list.append(department_id)
        selection_list.append(status_id)
    # 2 запрос
    selection_list.append(current_user_id)
    if filters is not None:
        selection_list.append(workspace_id)
        selection_list.append(department_id)
        selection_list.append(status_id)

    projects_qs = Project.objects.filter(id__in=RawSQL(request_text, selection_list))

    return projects_qs

# Получим список id рабочих пространств
def get_user_workspaces_list(current_user):

    workspace_list = []
    user_workspaces = current_user.related_workspace_members.all()
    for item_workspace in user_workspaces:
        workspace_list.append(item_workspace.workspace.id)

    return workspace_list
