import datetime
import locale
from task.models import Project, Task
from task.logic import common_logic

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))


def create_project_filters_dict(current_user) -> dict:

    filters_data: dict = {
        'current_user': current_user,
        'start_date': None,
        'end_date': None,
        'workspace_id': None,
        'department_id': None,
        'check_1_my_projects': False,
        'owner_id': None,
        'is_active': None,
        'is_completed': None,
        'status_id': None
    }

    return filters_data


def get_form_project_filters(filters, filters_data) -> dict:

    current_user = filters['current_user']
    selections = filters['selection_data']
    quick_selections = filters['quick_selection']

    type_of_period = quick_selections['period']
    end_date = datetime.date.today() if type_of_period != 'clean_period' else None
    start_date = common_logic.get_start_date(type_of_period, end_date) if type_of_period != 'clean_period' else None

    workspace_id = selections['workspace'] if selections['workspace'] != "" else None
    department_id = selections['department'] if selections['department'] != "" else None

    is_active = quick_selections['is_active']
    is_completed = quick_selections['is_completed']
    status_id = selections['status'] if selections['status'] != "" else None

    check_1_my_projects = quick_selections['check_1_my_projects']

    if check_1_my_projects is True:
        owner_id = current_user
    else:
        owner_id = selections['owner'] if selections['owner'] != "" else None

    filters_data['start_date'] = start_date
    filters_data['end_date'] = end_date
    filters_data['workspace_id'] = workspace_id
    filters_data['department_id'] = department_id
    filters_data['check_1_my_projects'] = check_1_my_projects
    filters_data['owner_id'] = owner_id
    filters_data['is_active'] = is_active
    filters_data['is_completed'] = is_completed
    filters_data['status_id'] = status_id

    return filters_data


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


def get_project_seriales_data(projects_qs, projects) -> list:

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


# Получим проекты и задачи пользователя с полными правами
def get_user_projects_and_tasks_full_rights(projects, filters_data) -> list:

    request_text = '''

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
    LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = %(current_user)s) task_new_messages
    ON tasks.id = task_new_messages.task_id
    
    WHERE
        projects.id > 0
        AND (%(start_date)s IS NULL OR created_at >= %(start_date)s)
        AND (%(end_date)s IS NULL OR created_at <= %(end_date)s)
        AND (%(workspace_id)s IS NULL OR workspace_id = %(workspace_id)s)
        AND (%(department_id)s IS NULL OR department_id = %(department_id)s)
        AND CASE 
                WHEN %(is_active)s IS TRUE THEN status_id = 1
                WHEN %(is_completed)s IS TRUE THEN status_id = 2
                ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
            END
        AND CASE 
                WHEN  %(check_1_my_projects)s IS FALSE THEN (%(owner_id)s IS NULL OR owner_id = %(owner_id)s)
                ELSE owner_id = %(current_user)s
            END             
            
    ORDER BY 
        projects.id,
        tasks.id                          

    '''

    print(filters_data)
    projects_qs = Project.objects.raw(request_text, params=filters_data)
    projects = get_project_seriales_data(projects_qs, projects)

    return projects


# Получим проекты и задачи пользователя с обычными правами
def get_user_projects_and_tasks(projects, filters_data) -> list:

    request_text = '''

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
                projects.owner_id = %(current_user)s      
            
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
                AND project_members.user_id = %(current_user)s
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
                    tasks.owner_id = %(current_user)s or tasks.executor_id = %(current_user)s               
                
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
                    AND task_members.user_id = %(current_user)s) all_tasks_user        
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
    LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = %(current_user)s) task_new_messages
    ON tasks.id = task_new_messages.task_id
    WHERE
        projects.id > 0
        AND (%(start_date)s IS NULL OR created_at >= %(start_date)s)
        AND (%(end_date)s IS NULL OR created_at <= %(end_date)s)
        AND (%(workspace_id)s IS NULL OR workspace_id = %(workspace_id)s)
        AND (%(department_id)s IS NULL OR department_id = %(department_id)s)
        AND CASE 
                WHEN %(is_active)s IS TRUE THEN status_id = 1
                WHEN %(is_completed)s IS TRUE THEN status_id = 2
                ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
            END
        AND CASE 
                WHEN  %(check_1_my_projects)s IS FALSE THEN (%(owner_id)s IS NULL OR owner_id = %(owner_id)s)
                ELSE owner_id = %(current_user)s
            END
    ORDER BY 
        projects.id,
        tasks.id                          

    '''

    projects_qs = Project.objects.raw(request_text, params=filters_data)
    projects = get_project_seriales_data(projects_qs, projects)

    return projects


# Получим данные по проектам, где пользователь является участником проекта (check_2)
def get_project_members(projects, filters_data, user_right) -> list:

    if user_right.is_full:

        request_text = '''
    
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
                AND project_members.user_id = %(current_user)s
                AND (%(start_date)s IS NULL OR projects.created_at >= %(start_date)s)
                AND (%(end_date)s IS NULL OR projects.created_at <= %(end_date)s)
                AND (%(workspace_id)s IS NULL OR projects.workspace_id = %(workspace_id)s)
                AND (%(department_id)s IS NULL OR projects.department_id = %(department_id)s)                
                AND CASE 
                        WHEN %(is_active)s IS TRUE THEN projects.status_id = 1
                        WHEN %(is_completed)s IS TRUE THEN projects.status_id = 2
                        ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
                    END                
                AND CASE 
                        WHEN  %(check_1_my_projects)s IS FALSE THEN (%(owner_id)s IS NULL OR projects.owner_id = %(owner_id)s)
                        ELSE owner_id = %(current_user)s
                    END
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
        LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = %(current_user)s) task_new_messages
        ON tasks.id = task_new_messages.task_id 

        ORDER BY 
            projects.id,
            tasks.id                          

        '''

    else:

        request_text = '''

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
                AND project_members.user_id = %(current_user)s
                AND (%(start_date)s IS NULL OR projects.created_at >= %(start_date)s)
                AND (%(end_date)s IS NULL OR projects.created_at <= %(end_date)s)
                AND (%(workspace_id)s IS NULL OR projects.workspace_id = %(workspace_id)s)
                AND (%(department_id)s IS NULL OR projects.department_id = %(department_id)s)                
                AND CASE 
                        WHEN %(is_active)s IS TRUE THEN projects.status_id = 1
                        WHEN %(is_completed)s IS TRUE THEN projects.status_id = 2
                        ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
                    END                
                AND CASE 
                        WHEN  %(check_1_my_projects)s IS FALSE THEN (%(owner_id)s IS NULL OR projects.owner_id = %(owner_id)s)
                        ELSE owner_id = %(current_user)s
                    END

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
                        tasks.owner_id = %(current_user)s or tasks.executor_id = %(current_user)s                

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
                        AND task_members.user_id = %(current_user)s) all_tasks_user        
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
        LEFT JOIN (SELECT * FROM task_task_new_messages WHERE user_id = %(current_user)s) task_new_messages
        ON tasks.id = task_new_messages.task_id 

        ORDER BY 
            projects.id,
            tasks.id                          

        '''

    projects_qs = Project.objects.raw(request_text, params=filters_data)
    projects: list = get_project_seriales_data(projects_qs, projects)

    return projects


# Все задачи по проекту, которые доступны пользователю (для view_project_tasks)
def get_user_project_tasks(project_id, current_user_id):

    request_text = '''
    
    select 
        all_tasks_user.id
    FROM        

    (select 
        tasks.id as id   
    FROM 
        task_task tasks                
    WHERE
        tasks.project_id = %(project_id)s 
        AND (tasks.owner_id = %(current_user_id)s or tasks.executor_id = %(current_user_id)s)                

    UNION ALL

    select 
        tasks.id
    FROM
        task_task tasks, 
        task_task_members task_members                                   
    WHERE
        tasks.project_id = %(project_id)s
        AND task_members.task_id = tasks.id                                  
        AND task_members.user_id = %(current_user_id)s) as all_tasks_user  

    GROUP by
        all_tasks_user.id               

    '''

    filters_data: dict = {
        'project_id': project_id,
        'current_user_id': current_user_id        
    }

    project_tasks_qs = Task.objects.raw(request_text, params=filters_data)

    return project_tasks_qs
