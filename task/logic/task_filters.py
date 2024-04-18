import datetime
from django.db.models import F
from task.models import Task, Task_Members, Task_New_Messages
from task.logic import common_logic


 # Обновим счетчики непрочитанных сообщений
def add_task_count_messages(task, user):

    users_to_notify = []
    members = Task_Members.objects.filter(task=task)
    for current_member in members:
        if current_member.user != user:
            if current_member.user not in users_to_notify:
                users_to_notify.append(current_member.user)

    if task.owner != user:
        if task.owner not in users_to_notify:
            users_to_notify.append(task.owner)

    if task.executor != user:
        if task.executor not in users_to_notify:
            users_to_notify.append(task.executor)

    if len(users_to_notify) > 0:
        for current_user in users_to_notify:
            current_counter = Task_New_Messages.objects.filter(task=task, user=current_user).first()
            if current_counter is None:
                Task_New_Messages.objects.create(task=task, user=current_user, new_messages=1)
            else:
                current_counter.new_messages = F('new_messages') + 1
                current_counter.save()


def clean_task_count_messages(task, user):
    current_counter = Task_New_Messages.objects.filter(task=task, user=user).first()
    if current_counter is not None:
        current_counter.new_messages = 0
        current_counter.save()


def get_tasks_seriales_data(tasks, tasks_qs, type_table, current_user_id) -> list:

    for item in tasks_qs:

        if type_table == "task":
            task = item
        elif type_table == "task_members":
            task = item.task

        task_to_add = {
            'id': task.id,
            'title': task.title,
            'url': task.get_absolute_url_main(),
            'status': task.status.title,
            'owner': f"{task.owner.last_name} {task.owner.first_name}",
            'executor': f"{task.executor.last_name} {task.executor.first_name}",
            'created_at': task.created_at,
            'project': task.project.title if task.project else '',
            'workspace': task.workspace.title,
            'department': task.department.title,
            'new_messages': 0
        }

        new_message = Task_New_Messages.objects.filter(task__id=task.id, user__id=current_user_id).first()
        if new_message:
            task_to_add['new_messages'] = new_message.new_messages

        # Проверяем есть ли уже такая задача в списке, если нет, добавляем
        if task_to_add not in tasks:
            tasks.append(task_to_add)

    return tasks


def get_form_task_filters(filters) -> dict:

    current_user = filters['current_user']
    selections = filters['selection_data']
    quick_selections = filters['quick_selection']

    type_of_period = quick_selections['period']
    end_date = datetime.date.today() if type_of_period != 'clean_period' else None
    start_date = common_logic.get_start_date(type_of_period, end_date) if type_of_period != 'clean_period' else None

    workspace_id = selections['workspace'] if selections['workspace'] != "" else None
    department_id = selections['department'] if selections['department'] != "" else None
    project_id = selections['project'] if selections['project'] != "" else None

    is_active = quick_selections['is_active']
    is_completed = quick_selections['is_completed']
    status_id = selections['status'] if selections['status'] != "" else None

    check_1_my_tasks = quick_selections['check_1_my_tasks']
    check_2_tasks_to_complete = quick_selections['check_2_tasks_to_complete']

    if check_1_my_tasks is True:
        owner_id = current_user
    else:
        owner_id = selections['owner'] if selections['owner'] != "" else None

    if check_2_tasks_to_complete is True:
        executor_id = current_user
    else:
        executor_id = selections['executor'] if selections['executor'] != "" else None

    filters_data: dict = {
        'current_user': current_user,
        'start_date': start_date,
        'end_date': end_date,
        'workspace_id': workspace_id,
        'department_id': department_id,
        'project_id': project_id,
        'check_1_my_tasks': check_1_my_tasks,
        'check_2_tasks_to_complete': check_2_tasks_to_complete,        
        'owner_id': owner_id,
        'executor_id': executor_id,
        'is_active': is_active,
        'is_completed': is_completed,
        'status_id': status_id
    }

    return filters_data


# Получим задачи пользователя по умолчанию (для GET)
def get_user_tasks(current_user_id):

    request_text = '''

    select 
        all_tasks_user.id
    FROM        

    (select 
        tasks.id as id   
    FROM 
        task_task tasks                
    WHERE
        tasks.owner_id = %(current_user)s or tasks.executor_id = %(current_user)s                

    UNION ALL

    select 
        tasks.id
    FROM 
        task_task_members task_members,
        task_task tasks               
    WHERE
        task_members.task_id = tasks.id                
        AND task_members.user_id = %(current_user)s) as all_tasks_user  

    GROUP by
        all_tasks_user.id              

    '''

    selections: dict = {'current_user': current_user_id}

    tasks_members_qs = Task.objects.raw(request_text, params=selections)

    return tasks_members_qs


# Получим задачи пользователя c учетом селекторов
def get_user_tasks_selection(filters_data, user_right):

    if user_right.is_full:

        request_text = '''

        SELECT        
            task_task.id
        FROM task_task  

        WHERE
            id > 0                 
            AND (%(start_date)s IS NULL OR created_at >= %(start_date)s)
            AND (%(end_date)s IS NULL OR created_at <= %(end_date)s)
            AND (%(workspace_id)s IS NULL OR workspace_id = %(workspace_id)s)
            AND (%(department_id)s IS NULL OR department_id = %(department_id)s)
            AND (%(project_id)s IS NULL OR project_id = %(project_id)s)
            AND CASE 
                    WHEN %(check_1_my_tasks)s IS TRUE AND %(check_2_tasks_to_complete)s IS TRUE 
                    THEN (owner_id = %(current_user)s or executor_id = %(current_user)s)
                    ELSE            
                        CASE 
                            WHEN  %(check_1_my_tasks)s IS FALSE THEN (%(owner_id)s IS NULL OR owner_id = %(owner_id)s)
                            ELSE owner_id = %(current_user)s
                        END            
                        AND CASE 
                                WHEN  %(check_2_tasks_to_complete)s IS FALSE THEN (%(executor_id)s IS NULL OR executor_id = %(executor_id)s)
                                ELSE executor_id = %(current_user)s
                            END
                END           
            AND CASE 
                    WHEN %(is_active)s IS TRUE THEN status_id in (1,2)
                    WHEN %(is_completed)s IS TRUE THEN status_id in (3,5)
                    ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
                END            
        '''

    else:

        request_text = '''
        
        SELECT        
            task_task.id
        FROM task_task  
        
        WHERE 
            id in (SELECT 
                    all_tasks_user.id as id
                    FROM
                        (select 
                            tasks.id as id   
                        FROM 
                            task_task tasks                
                        WHERE
                            tasks.owner_id = %(current_user)s or tasks.executor_id = %(current_user)s                
            
                        UNION ALL
            
                        select 
                            tasks.id
                        FROM 
                            task_task_members task_members,
                            task_task tasks               
                        WHERE
                            task_members.task_id = tasks.id                
                            AND task_members.user_id = %(current_user)s) as all_tasks_user
                    GROUP by
                        all_tasks_user.id)
            AND (%(start_date)s IS NULL OR created_at >= %(start_date)s)
            AND (%(end_date)s IS NULL OR created_at <= %(end_date)s)
            AND (%(workspace_id)s IS NULL OR workspace_id = %(workspace_id)s)
            AND (%(department_id)s IS NULL OR department_id = %(department_id)s)
            AND (%(project_id)s IS NULL OR project_id = %(project_id)s)
            AND CASE 
                    WHEN %(check_1_my_tasks)s IS TRUE AND %(check_2_tasks_to_complete)s IS TRUE 
                    THEN (owner_id = %(current_user)s or executor_id = %(current_user)s)
                    ELSE            
                        CASE 
                            WHEN  %(check_1_my_tasks)s IS FALSE THEN (%(owner_id)s IS NULL OR owner_id = %(owner_id)s)
                            ELSE owner_id = %(current_user)s
                        END            
                        AND CASE 
                                WHEN  %(check_2_tasks_to_complete)s IS FALSE THEN (%(executor_id)s IS NULL OR executor_id = %(executor_id)s)
                                ELSE executor_id = %(current_user)s
                            END
                END             
            AND CASE 
                    WHEN %(is_active)s IS TRUE THEN status_id in (1,2)
                    WHEN %(is_completed)s IS TRUE THEN status_id in (3,5)
                    ELSE (%(status_id)s IS NULL OR status_id = %(status_id)s)
                END        

        '''

    tasks_qs = Task.objects.raw(request_text, params=filters_data)

    return tasks_qs


# Получим задачи где пользователь является участником задачи
def get_task_members(filters_data):

    request_text = '''
        SELECT 
            taskmembers.id,
            taskmembers.task_id
        FROM 
            task_task_members taskmembers,
            task_task tasks
        WHERE
            taskmembers.task_id = tasks.id
            AND taskmembers.user_id = %(current_user)s
            AND (%(start_date)s IS NULL OR tasks.created_at >= %(start_date)s)
            AND (%(end_date)s IS NULL OR tasks.created_at <= %(end_date)s)
            AND (%(workspace_id)s IS NULL OR tasks.workspace_id = %(workspace_id)s)
            AND (%(department_id)s IS NULL OR tasks.department_id = %(department_id)s)
            AND (%(project_id)s IS NULL OR tasks.project_id = %(project_id)s)
            AND CASE 
                    WHEN  %(check_1_my_tasks)s IS FALSE THEN (%(owner_id)s IS NULL OR tasks.owner_id = %(owner_id)s)
                    ELSE tasks.owner_id IS NOT NULL
                END
            AND CASE 
                    WHEN  %(check_2_tasks_to_complete)s IS FALSE THEN (%(executor_id)s IS NULL OR tasks.executor_id = %(executor_id)s)
                    ELSE tasks.executor_id IS NOT NULL
                END            
            AND CASE 
                    WHEN %(is_active)s IS TRUE THEN tasks.status_id in (1,2)
                    WHEN %(is_completed)s IS TRUE THEN tasks.status_id in (3,5)
                    ELSE (%(status_id)s IS NULL OR tasks.status_id = %(status_id)s)
                END
        GROUP by
            taskmembers.id,
            taskmembers.task_id
    '''

    tasks_members_qs = Task_Members.objects.raw(request_text, params=filters_data)

    return tasks_members_qs
