import datetime
import locale
from task.models import Project, Task
from task.logic import common_filters

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

# Все задачи по проекту, которые доступны пользователю (для view_project_tasks)
def get_user_project_tasks(project_id, current_user_id):

    request_text = """
    
    select 
        all_tasks_user.id
    FROM        

    (select 
        tasks.id as id   
    FROM 
        task_task tasks                
    WHERE
        tasks.project_id = %s 
        AND (tasks.owner_id = %s or tasks.executor_id = %s)                

    UNION ALL

    select 
        tasks.id
    FROM
        task_task tasks, 
        task_task_members task_members                                   
    WHERE
        tasks.project_id = %s
        AND task_members.task_id = tasks.id                                  
        AND task_members.user_id = %s) as all_tasks_user  

    GROUP by
        all_tasks_user.id               

    """

    selection_list = []
    selection_list.append(project_id)
    selection_list.append(current_user_id)
    selection_list.append(current_user_id)
    selection_list.append(project_id)
    selection_list.append(current_user_id)

    project_tasks_qs = Task.objects.raw(request_text, selection_list)

    return project_tasks_qs

def create_project_row(item):

    project_to_add = {
        'id': item.id,
        'title': item.title,
        'url': f"/projects/{item.id}/main/",
        'status': item.status.title,
        'owner': f"{item.owner.last_name} {item.owner.first_name}",
        'created_at': item.created_at,
        'workspace': item.workspace.title,
        'department': item.department.title
    }

    return project_to_add

def create_task_row(item):

    task_to_add = {
        'id': item.task_id,
        'title': item.task_title,
        'url': f"/tasks/{item.task_id}/main/",
        'status': item.task_status,
        'owner': f"{item.task_owner_last_name} {item.task_owner_first_name}",
        'executor': f"{item.executor_last_name} {item.executor_first_name}",
        'created_at': item.created_at,
        'new_messages': item.task_new_messages
    }

    return task_to_add

def get_final_projects_table(projects_qs, projects):

    first_row = True
    for item in projects_qs:

        if first_row:

            project_to_add = create_project_row(item)
            project_tasks = []

            if item.task_id is not None:
                task_to_add = create_task_row(item)
                project_tasks.append(task_to_add)

            temp_project_id = item.id
            first_row = False
            continue

        if item.id == temp_project_id:
            if item.task_id is not None:
                task_to_add = create_task_row(item)
                project_tasks.append(task_to_add)
        else:

            # Проверяем есть ли уже такой проект в списке, если нет, добвляем
            project_to_add['tasks'] = project_tasks
            if project_to_add not in projects:
                projects.append(project_to_add)

            project_to_add = create_project_row(item)
            project_tasks = []

            temp_project_id = item.id

            if item.task_id is not None:
                task_to_add = create_task_row(item)
                project_tasks.append(task_to_add)

    # Проверяем есть ли уже такой проект в списке, если нет, добавляем
    if not first_row:
        project_to_add['tasks'] = project_tasks
        if project_to_add not in projects:
            projects.append(project_to_add)

    return projects

# Получим проекты и задачи пользователя с полными правами по умолчанию (для GET)
def get_user_projects_and_tasks_full_rights(projects, current_user_id, selection_line, selection_list):

    request_text = f"""

    SELECT        
        projects.id,
        tasks.id as task_id,
        tasks.title as task_title,
        tasks.status as task_status,
        tasks.owner_last_name as task_owner_last_name,
        tasks.owner_first_name as task_owner_first_name,
        tasks.executor_last_name as executor_last_name,
        tasks.executor_first_name as executor_first_name,
        task_new_messages.new_messages as task_new_messages         
        
    FROM task_project projects
    LEFT JOIN (
        SELECT
            t_task.id as id,
            t_task.title as title,
            t_status.title as status,
            t_task.project_id as project_id,  
            CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.last_name END as owner_last_name,
            CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.first_name END as owner_first_name,
            CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.last_name END as executor_last_name,
            CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.first_name END as executor_first_name
        FROM 
            task_task t_task,
            task_task_status t_status,
            auth_user t_user_owner,
            auth_user t_user_executor
        WHERE
            t_task.status_id = t_status.id
            AND t_task.owner_id = t_user_owner.id
            AND t_task.executor_id = t_user_executor.id   
        ) tasks  
    ON projects.id = tasks.project_id 
    LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = {current_user_id}) task_new_messages
    ON tasks.id = task_new_messages.task_id
    
    {selection_line} 
            
    ORDER BY 
        projects.id,
        tasks.id                          

    """

    projects_qs = Project.objects.raw(request_text, selection_list)

    projects = get_final_projects_table(projects_qs, projects)

    return projects

# Получим проекты и задачи пользователя с обычными правами по умолчанию (для GET)
def get_user_projects_and_tasks(current_user_id, selection_line, selection_list):

    request_text = f"""

    SELECT        
        projects.id,            
        tasks.id as task_id,
        tasks.title as task_title,
        tasks.status as task_status,
        tasks.owner_last_name as task_owner_last_name,
        tasks.owner_first_name as task_owner_first_name,
        tasks.executor_last_name as executor_last_name,
        tasks.executor_first_name as executor_first_name,
        task_new_messages.new_messages as task_new_messages         
    
    FROM (
        select 
            all_projects_user.id,
            all_projects_user.workspace_id as workspace_id,
            all_projects_user.department_id as department_id,
            all_projects_user.status_id as status_id,
            all_projects_user.owner_id as owner_id,
            all_projects_user.created_at
        FROM 
            (select 
                projects.id as id,
                projects.workspace_id as workspace_id,
                projects.department_id as department_id,
                projects.status_id as status_id,
                projects.owner_id as owner_id,
                projects.created_at as created_at   
            FROM 
                task_project projects                
            WHERE
                projects.owner_id = {current_user_id}      
            
            UNION ALL
            
            select 
                projects.id,
                projects.workspace_id,
                projects.department_id,
                projects.status_id,
                projects.owner_id,
                projects.created_at    
            FROM 
                task_project_members project_members,
                task_project projects               
            WHERE
                project_members.project_id = projects.id                
                AND project_members.user_id = {current_user_id}
            ) as all_projects_user               
            
        GROUP by
            all_projects_user.id,
            all_projects_user.workspace_id,
            all_projects_user.department_id,
            all_projects_user.status_id,
            all_projects_user.owner_id,
            all_projects_user.created_at
            ) projects
    LEFT JOIN (
        SELECT
            t_task.id as id,
            t_task.title as title,
            t_status.title as status,
            t_task.project_id as project_id,  
            CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.last_name END as owner_last_name,
            CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.first_name END as owner_first_name,
            CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.last_name END as executor_last_name,
            CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.first_name END as executor_first_name
        FROM         
            (select 
                all_tasks_user.id,
                all_tasks_user.title,
                all_tasks_user.project_id,
                all_tasks_user.owner_id,
                all_tasks_user.executor_id,
                all_tasks_user.status_id                    
            FROM           
                (select 
                    tasks.id as id,
                    tasks.title as title,
                    tasks.project_id as project_id,
                    tasks.owner_id as owner_id,
                    tasks.executor_id as executor_id,
                    tasks.status_id as status_id
                FROM 
                    task_task tasks                
                WHERE
                    tasks.owner_id = {current_user_id} or tasks.executor_id = {current_user_id}                
                
                UNION ALL
                
                select 
                    tasks.id,
                    tasks.title,
                    tasks.project_id,
                    tasks.owner_id,
                    tasks.executor_id,
                    tasks.status_id
                FROM 
                    task_task_members task_members,
                    task_task tasks               
                WHERE
                    task_members.task_id = tasks.id                
                    AND task_members.user_id = {current_user_id}) all_tasks_user        
            GROUP by
                    all_tasks_user.id,
                    all_tasks_user.title,
                    all_tasks_user.project_id,
                    all_tasks_user.owner_id,
                    all_tasks_user.executor_id,
                    all_tasks_user.status_id                    
                    ) t_task,
            task_task_status t_status,
            auth_user t_user_owner,
            auth_user t_user_executor
        WHERE
            t_task.status_id = t_status.id
            AND t_task.owner_id = t_user_owner.id
            AND t_task.executor_id = t_user_executor.id   
        ) tasks  
    ON projects.id = tasks.project_id 
    LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = {current_user_id}) task_new_messages
    ON tasks.id = task_new_messages.task_id 
    
    {selection_line}
    
    ORDER BY 
        projects.id,
        tasks.id                          

    """

    projects_qs = Project.objects.raw(request_text, selection_list)
    projects = get_final_projects_table(projects_qs, [])

    return projects

# Получим данные по проектам, где пользовтаель является участником проекта (check_2)
def get_project_members(filters, current_user_id, user_right_id, projects):

    selection_list = []

    type_of_period = filters['quick_selection']['period']

    if type_of_period != 'clean_period':
        end_date = datetime.date.today()
        start_date = common_filters.get_start_date(type_of_period, end_date)
        selection_list.append(start_date)
        selection_list.append(end_date)

    workspace_id = filters['selection_data']['workspace']
    if workspace_id != "":
        selection_list.append(workspace_id)

    department_id = filters['selection_data']['department']
    if department_id != "":
        selection_list.append(department_id)

    is_active = filters['quick_selection']['is_active']
    is_completed = filters['quick_selection']['is_completed']

    selection_status = ''
    if is_active is True:
        selection_status = ' AND projects.status_id = 1 '
    elif is_completed is True:
        selection_status = ' AND projects.status_id = 2 '
    else:
        status_id = filters['selection_data']['status']
        if status_id != "":
            selection_status = 'AND projects.status_id = %s'
            selection_list.append(status_id)

    check_1 = filters['quick_selection']['check_1']
    # check_2 = filters['quick_selection']['check_2']

    owner_id = filters['selection_data']['owner']
    if check_1 is not True:
        if owner_id != "":
            selection_list.append(owner_id)

    if user_right_id == 1:

        request_text = f"""
    
        SELECT        
            projects.id,            
            tasks.id as task_id,
            tasks.title as task_title,
            tasks.status as task_status,
            tasks.owner_last_name as task_owner_last_name,
            tasks.owner_first_name as task_owner_first_name,
            tasks.executor_last_name as executor_last_name,
            tasks.executor_first_name as executor_first_name,
            task_new_messages.new_messages as task_new_messages         

        FROM (
            select 
                projects.id as id,
                projects.workspace_id as workspace_id,
                projects.department_id as department_id,
                projects.status_id as status_id,
                projects.owner_id as owner_id,
                projects.created_at as created_at    
            FROM 
                task_project_members project_members,
                task_project projects               
            WHERE
                project_members.project_id = projects.id                
                AND project_members.user_id = {current_user_id}
                {'AND projects.created_at BETWEEN %s AND %s' if type_of_period != 'clean_period' else ''}  
                {'AND projects.workspace_id = %s' if workspace_id != "" else ''}    
                {'AND projects.department_id = %s' if department_id != "" else ''} 
                {selection_status if selection_status != '' else ''}                      
                {'AND projects.owner_id = %s' if owner_id != "" else ''}

                GROUP by
                    projects.id 

                ) as projects
        LEFT JOIN (
            SELECT
                t_task.id as id,
                t_task.title as title,
                t_status.title as status,
                t_task.project_id as project_id,  
                CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.last_name END as owner_last_name,
                CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.first_name END as owner_first_name,
                CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.last_name END as executor_last_name,
                CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.first_name END as executor_first_name
            FROM                
                task_task t_task,
                task_task_status t_status,
                auth_user t_user_owner,
                auth_user t_user_executor
            WHERE
                t_task.status_id = t_status.id
                AND t_task.owner_id = t_user_owner.id
                AND t_task.executor_id = t_user_executor.id   
            ) tasks  
        ON projects.id = tasks.project_id 
        LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = {current_user_id}) task_new_messages
        ON tasks.id = task_new_messages.task_id 

        ORDER BY 
            projects.id,
            tasks.id                          

        """

    else:

        request_text = f"""

        SELECT        
            projects.id,            
            tasks.id as task_id,
            tasks.title as task_title,
            tasks.status as task_status,
            tasks.owner_last_name as task_owner_last_name,
            tasks.owner_first_name as task_owner_first_name,
            tasks.executor_last_name as executor_last_name,
            tasks.executor_first_name as executor_first_name,
            task_new_messages.new_messages as task_new_messages         

        FROM (
            select 
                projects.id as id,
                projects.workspace_id as workspace_id,
                projects.department_id as department_id,
                projects.status_id as status_id,
                projects.owner_id as owner_id,
                projects.created_at as created_at    
            FROM 
                task_project_members project_members,
                task_project projects               
            WHERE
                project_members.project_id = projects.id                
                AND project_members.user_id = {current_user_id}
                {'AND projects.created_at BETWEEN %s AND %s' if type_of_period != 'clean_period' else ''}  
                {'AND projects.workspace_id = %s' if workspace_id != "" else ''}    
                {'AND projects.department_id = %s' if department_id != "" else ''} 
                {selection_status if selection_status != '' else ''}                      
                {'AND projects.owner_id = %s' if owner_id != "" else ''}

                GROUP by
                    projects.id 

                ) as projects
        LEFT JOIN (
            SELECT
                t_task.id as id,
                t_task.title as title,
                t_status.title as status,
                t_task.project_id as project_id,  
                CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.last_name END as owner_last_name,
                CASE WHEN t_task.owner_id = t_user_owner.id THEN t_user_owner.first_name END as owner_first_name,
                CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.last_name END as executor_last_name,
                CASE WHEN t_task.executor_id = t_user_executor.id THEN t_user_executor.first_name END as executor_first_name
            FROM         
                (select 
                    all_tasks_user.id,
                    all_tasks_user.title,
                    all_tasks_user.project_id,
                    all_tasks_user.owner_id,
                    all_tasks_user.executor_id,
                    all_tasks_user.status_id                    
                FROM           
                    (select 
                        tasks.id as id,
                        tasks.title as title,
                        tasks.project_id as project_id,
                        tasks.owner_id as owner_id,
                        tasks.executor_id as executor_id,
                        tasks.status_id as status_id
                    FROM 
                        task_task tasks                
                    WHERE
                        tasks.owner_id = {current_user_id} or tasks.executor_id = {current_user_id}                

                    UNION ALL

                    select 
                        tasks.id,
                        tasks.title,
                        tasks.project_id,
                        tasks.owner_id,
                        tasks.executor_id,
                        tasks.status_id
                    FROM 
                        task_task_members task_members,
                        task_task tasks               
                    WHERE
                        task_members.task_id = tasks.id                
                        AND task_members.user_id = {current_user_id}) all_tasks_user        
                GROUP by
                        all_tasks_user.id) t_task,
                task_task_status t_status,
                auth_user t_user_owner,
                auth_user t_user_executor
            WHERE
                t_task.status_id = t_status.id
                AND t_task.owner_id = t_user_owner.id
                AND t_task.executor_id = t_user_executor.id   
            ) tasks  
        ON projects.id = tasks.project_id 
        LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = {current_user_id}) task_new_messages
        ON tasks.id = task_new_messages.task_id 

        ORDER BY 
            projects.id,
            tasks.id                          

        """

    # print(request_text)

    projects_qs = Project.objects.raw(request_text, selection_list)
    projects = get_final_projects_table(projects_qs, projects)

    return projects
