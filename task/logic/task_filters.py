import datetime
from django.db.models import F
from task.models import Task, Task_Members, Task_New_Messages


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


def get_tasks_table(current_user_id: int, tasks: list[Task_New_Messages]) -> list:
    task_list = []

    for task in tasks:

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

        new_messages = Task_New_Messages.objects.filter(task__id=task.id, user__id=current_user_id)
        if new_messages.count() > 0:
            task_to_add['new_messages'] = new_messages[0].new_messages

        task_list.append(task_to_add)

    return task_list


def get_tasks_final_table(vu_tasks, vu_tasks_qs, type_table, current_user_id):
    for item in vu_tasks_qs:

        if type_table == "task":
            task = item
        elif type_table == "task_members":
            task = item.task

        task_to_add = {
            'id': task.id,
            'title': task.title,
            'url': Task.get_absolute_url_main(task),
            'status': task.status.title,
            'owner': f"{task.executor.last_name} {task.executor.first_name}",
            'executor': f"{task.executor.last_name} {task.executor.first_name}",
            'created_at': task.created_at,
            'project': task.project.title if task.project else '',
            'workspace': task.workspace.title,
            'department': task.department.title,
            'new_messages': 0
        }

        new_messages = Task_New_Messages.objects.filter(task__id=task.id, user__id=current_user_id)
        if new_messages.count() > 0:
            task_to_add['new_messages'] = new_messages[0].new_messages

        # Проверяем есть ли уже такая задача в списке, если нет, добавляем
        if task_to_add not in vu_tasks:
            vu_tasks.append(task_to_add)

    return vu_tasks


# Получим задачи пользователя по умолчанию (для GET)
def get_user_tasks(current_user_id):
    request_text = """

    select 
        all_tasks_user.id
    FROM        

    (select 
        tasks.id as id   
    FROM 
        task_task tasks                
    WHERE
        tasks.owner_id = %s or tasks.executor_id = %s                

    UNION ALL

    select 
        tasks.id
    FROM 
        task_task_members task_members,
        task_task tasks               
    WHERE
        task_members.task_id = tasks.id                
        AND task_members.user_id = %s) as all_tasks_user  

    GROUP by
        all_tasks_user.id              

    """

    selection_list = []
    selection_list.append(current_user_id)
    selection_list.append(current_user_id)
    selection_list.append(current_user_id)

    tasks_members_qs = Task.objects.raw(request_text, selection_list)

    return tasks_members_qs


# Получим задачи пользователя c учетом селекторов
def get_user_tasks_selection(selection_line, selection_list_view, current_user_id, user_right):

    selection_list = []

    if user_right == 1:  # Полные права

        request_text = f"""

        SELECT        
            task_task.id
        FROM task_task  

        WHERE
            id > 0                 
            {selection_line}   
            
        """

    else:

        request_text = f"""
        
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
                            tasks.owner_id = %s or tasks.executor_id = %s                
            
                        UNION ALL
            
                        select 
                            tasks.id
                        FROM 
                            task_task_members task_members,
                            task_task tasks               
                        WHERE
                            task_members.task_id = tasks.id                
                            AND task_members.user_id = %s) as all_tasks_user
                    GROUP by
                        all_tasks_user.id)
            {selection_line}        

        """

        selection_list.append(current_user_id)
        selection_list.append(current_user_id)
        selection_list.append(current_user_id)

    selection_list += selection_list_view

    tasks_qs = Task.objects.raw(request_text, selection_list)

    return tasks_qs


# Функции получения списка задач
def get_start_date(type_of_period, end_date):
    if type_of_period == 'week':
        start_date = end_date - datetime.timedelta(days=7)
    elif type_of_period == 'month':
        start_date = end_date - datetime.timedelta(days=30)
    elif type_of_period == 'quarter':
        start_date = end_date - datetime.timedelta(days=90)
    elif type_of_period == 'year':
        start_date = end_date - datetime.timedelta(days=365)

    return start_date


def get_task_members(filters):
    selection_list = []

    type_of_period = filters['quick_selection']['period']

    if type_of_period != 'clean_period':
        end_date = datetime.date.today()
        start_date = get_start_date(type_of_period, end_date)
        selection_list.append(start_date)
        selection_list.append(end_date)

    # Добавляем в отбор текущего пользователя
    selection_list.append(filters['current_user'])

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
        selection_status = 'AND tasks.status_id in (1,2,4)'
    elif is_completed is True:
        selection_status = 'AND tasks.status_id in (3,5)'
    else:
        status_id = filters['selection_data']['status']
        if status_id != "":
            selection_status = 'AND tasks.status_id = %s'
            selection_list.append(status_id)

    project_id = filters['selection_data']['project']
    if project_id != "":
        selection_list.append(project_id)

    check_1 = filters['quick_selection']['check_1']
    check_2 = filters['quick_selection']['check_2']

    owner_id = filters['selection_data']['owner']
    if check_1 is not True:
        if owner_id != "":
            selection_list.append(owner_id)

    executor_id = filters['selection_data']['executor']
    if check_2 is not True:
        if executor_id != "":
            selection_list.append(executor_id)

    ### !!! id (первый селектор) обязательно должно быть тексте при ручном указании полей (не *)
    ### соединение сделано, что бы обратиться к полям задачи в условиия, в task_task_members к ним не обратиться
    request_text = f"""
                select 
                    taskmembers.id, 
                    taskmembers.task_id    
                FROM 
                    task_task_members taskmembers,
                    task_task tasks                
                WHERE
                    taskmembers.task_id = tasks.id
                    {'AND tasks.created_at BETWEEN %s AND %s' if type_of_period != 'clean_period' else ''}  
                    AND taskmembers.user_id = %s                      
                    {'AND tasks.workspace_id = %s' if workspace_id != "" else ''}    
                    {'AND tasks.department_id = %s' if department_id != "" else ''} 
                    {selection_status if selection_status != '' else ''}
                    {'AND tasks.project_id = %s' if project_id != "" else ''}
                    {'AND tasks.owner_id = %s' if owner_id != "" else ''}
                    {'AND tasks.executor_id = %s' if executor_id != "" else ''}
                GROUP by
                    taskmembers.id,
                    taskmembers.task_id                              
                """

    # print(request_text)

    tasks_members_qs = Task_Members.objects.raw(request_text, selection_list)
    # print("Выборка по Task_Members")
    # for task_item in tasks_members_qs:
    #     print(task_item.task.title, task_item.task.owner)

    return tasks_members_qs
