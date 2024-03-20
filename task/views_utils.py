from .models import Task, Project, Task_Dispute, Task_Members, Project_Members, User, User_Rights, Task_New_Messages, \
    Unauthorized_Access_Attempts
from django.db.models.expressions import RawSQL
from django.db.models import F

import os

import random
from random import randint

import datetime
import locale

# locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
locale.setlocale(locale.LC_ALL, ('ru_RU', 'UTF-8'))

# Функции общего назначения

months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
          'декабря']


def get_user_name(this_user):
    return '{} {}'.format(this_user.last_name, this_user.first_name)


def format_data(this_data):
    # return this_data.strftime("%d %b %Y в %H:%M")
    this_data_str = f'{this_data.day} {months[this_data.month - 1]} {this_data.year} в {this_data:%H:%M}'

    return this_data_str


# Функции получения списка задач

def vu_get_start_date(type_of_period, end_date):
    if type_of_period == 'week':
        start_date = end_date - datetime.timedelta(days=7)
    elif type_of_period == 'month':
        start_date = end_date - datetime.timedelta(days=30)
    elif type_of_period == 'quarter':
        start_date = end_date - datetime.timedelta(days=90)
    elif type_of_period == 'year':
        start_date = end_date - datetime.timedelta(days=365)

    return start_date


def vu_get_task_members(filters):
    selection_list = []

    type_of_period = filters['quick_selection']['period']

    if type_of_period != 'clean_period':
        end_date = datetime.date.today()
        start_date = vu_get_start_date(type_of_period, end_date)
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
    if is_active == True:
        selection_status = 'AND tasks.status_id in (1,2,4)'
    elif is_completed == True:
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
    if check_1 != True:
        if owner_id != "":
            selection_list.append(owner_id)

    executor_id = filters['selection_data']['executor']
    if check_2 != True:
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
                    taskmembers.task_id                              
                """

    # print(request_text)

    tasks_members_qs = Task_Members.objects.raw(request_text, selection_list)
    # print("Выборка по Task_Members")
    # for task_item in tasks_members_qs:
    #     print(task_item.task.title, task_item.task.owner)

    return tasks_members_qs


def vu_get_tasks_final_table(vu_tasks, vu_tasks_qs, type_table, current_user_id):
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
            'owner': '{} {}'.format(task.owner.last_name, task.owner.first_name),
            'executor': '{} {}'.format(task.executor.last_name, task.executor.first_name),
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


class User_Rights_Utils:

    def check_permissions_on_task(current_task, current_user):

        x = randint(1, 5)
        if x == 1:
            image_name = 'img/jack1.gif'
        else:
            image_name = f'img/jack{x}.jpeg'

        user_right = User_Rights.objects.get(user=current_user).role
        if user_right.id == 1:
            return {'image_name': image_name, 'access': True}

        have_access_to_task = False
        if current_task.owner == current_user or current_task.executor == current_user:
            have_access_to_task = True

        is_member_qs = Task_Members.objects.filter(task=current_task, user=current_user)
        if is_member_qs.count() > 0:
            have_access_to_task = True

        if have_access_to_task == False:
            Unauthorized_Access_Attempts.objects.create(url=current_task.get_absolute_url_main(), user=current_user)

        return {'image_name': image_name, 'access': have_access_to_task}

    def check_permissions_on_project(current_project, current_user):

        x = randint(1, 5)
        if x == 1:
            image_name = 'img/jack1.gif'
        else:
            image_name = f'img/jack{x}.jpeg'

        user_right = User_Rights.objects.get(user=current_user).role
        if user_right.id == 1:
            return {'image_name': image_name, 'access': True}

        have_access_to_project = False
        if current_project.owner == current_user:
            have_access_to_project = True

        is_member_qs = Project_Members.objects.filter(project=current_project, user=current_user)
        if is_member_qs.count() > 0:
            have_access_to_project = True

        if have_access_to_project == False:
            Unauthorized_Access_Attempts.objects.create(url=current_project.get_absolute_url_main(), user=current_user)

        return {'image_name': image_name, 'access': have_access_to_project}

    def get_input_right(type_form, item, user_id):

        if type_form == 'task':
            if item.project:
                if item.project.status.id == 2:
                    return {'department': False, 'executor': False, 'project': False, 'status': False,
                            'finish_date': False, 'button': False, 'members': False}
                else:
                    if item.status.id == 3:
                        return {'department': False, 'executor': False, 'project': False, 'status': False,
                                'finish_date': False, 'button': False, 'members': False}
            else:
                if item.status.id == 3 or item.status.id == 5:
                    return {'department': False, 'executor': False, 'project': False, 'status': False,
                            'finish_date': False, 'button': False, 'members': False}

            if item.owner.id == user_id:
                type_user = 'owner'
            elif item.executor.id == user_id:
                type_user = 'executor'
            else:
                type_user = 'member'

        if type_form == 'project':
            if item.status.id == 2:
                return {'department': False, 'executor': False, 'project': False, 'status': False,
                        'finish_date': False, 'button': False, 'members': False}

            if item.owner.id == user_id:
                type_user = 'owner'
            else:
                type_user = 'member'

        input_right = {}

        if type_form == 'task' or type_form == 'project':
            if type_user == 'owner':
                input_right['department'] = True
                input_right['status'] = True
                input_right['finish_date'] = True
                input_right['button'] = True
                input_right['members'] = True

            if type_user == 'executor':
                input_right['department'] = False
                input_right['status'] = True
                input_right['finish_date'] = True
                input_right['button'] = True
                input_right['members'] = False

            if type_user == 'member':
                input_right['department'] = False
                input_right['status'] = False
                input_right['finish_date'] = False
                input_right['button'] = False
                input_right['members'] = False

        if type_form == 'task':
            if type_user == 'owner':
                input_right['executor'] = True
                input_right['project'] = True
            else:
                input_right['executor'] = False
                input_right['project'] = False

        return input_right


class Selection_Utils:

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

        workspace_id = filters["workspace"] if filters != None else ""
        department_id = filters["department"] if filters != None else ""
        status_id = 1 if filters != None else ""

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
        if filters != None:
            selection_list.append(workspace_id)
            selection_list.append(department_id)
            selection_list.append(status_id)
        # 2 запрос
        selection_list.append(current_user_id)
        if filters != None:
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


class Project_Utils:

    # Все задачи по проекту, которые доступны пользователю (для view_project_tasks)
    def get_user_project_tasks(project_id, current_user_id):

        request_text = f"""            

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
            'owner': '{} {}'.format(item.owner.last_name, item.owner.first_name),
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
            'owner': '{} {}'.format(item.task_owner_last_name, item.task_owner_first_name),
            'executor': '{} {}'.format(item.executor_last_name, item.executor_first_name),
            'created_at': item.created_at,
            'new_messages': item.task_new_messages
        }

        return task_to_add

    def get_final_projects_table(projects_qs, projects):

        first_row = True
        for item in projects_qs:

            if first_row:

                project_to_add = Project_Utils.create_project_row(item)
                project_tasks = []

                if item.task_id != None:
                    task_to_add = Project_Utils.create_task_row(item)
                    project_tasks.append(task_to_add)

                temp_project_id = item.id
                first_row = False
                continue

            if item.id == temp_project_id:
                if item.task_id != None:
                    task_to_add = Project_Utils.create_task_row(item)
                    project_tasks.append(task_to_add)
            else:

                # Проверяем есть ли уже такой проект в списке, если нет, добвляем
                project_to_add['tasks'] = project_tasks
                if project_to_add not in projects:
                    projects.append(project_to_add)

                project_to_add = Project_Utils.create_project_row(item)
                project_tasks = []

                temp_project_id = item.id

                if item.task_id != None:
                    task_to_add = Project_Utils.create_task_row(item)
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

        projects = Project_Utils.get_final_projects_table(projects_qs, projects)

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
                all_projects_user.workspace_id,
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
                all_projects_user.id) projects
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
        
        {selection_line}
        
        ORDER BY 
            projects.id,
            tasks.id                          

       """

        projects_qs = Project.objects.raw(request_text, selection_list)
        projects = Project_Utils.get_final_projects_table(projects_qs, [])

        return projects

    # Получим данные по проектам, где пользовтаель является участником проекта (check_2)
    def get_project_members(filters, current_user_id, user_right_id, projects):

        selection_list = []

        type_of_period = filters['quick_selection']['period']

        if type_of_period != 'clean_period':
            end_date = datetime.date.today()
            start_date = vu_get_start_date(type_of_period, end_date)
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
        if is_active == True:
            selection_status = ' AND projects.status_id = 1 '
        elif is_completed == True:
            selection_status = ' AND projects.status_id = 2 '
        else:
            status_id = filters['selection_data']['status']
            if status_id != "":
                selection_status = 'AND projects.status_id = %s'
                selection_list.append(status_id)

        check_1 = filters['quick_selection']['check_1']
        check_2 = filters['quick_selection']['check_2']

        owner_id = filters['selection_data']['owner']
        if check_1 != True:
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
        projects = Project_Utils.get_final_projects_table(projects_qs, projects)

        return projects


class Task_Utils:

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
                if current_counter == None:
                    Task_New_Messages.objects.create(task=task, user=current_user, new_messages=1)
                else:
                    current_counter.new_messages = F('new_messages') + 1
                    current_counter.save()

    def clean_task_count_messages(task, user):
        current_counter = Task_New_Messages.objects.filter(task=task, user=user).first()
        if current_counter != None:
            current_counter.new_messages = 0
            current_counter.save()

    def get_tasks_table(current_user_id, tasks):

        task_list = []

        for task in tasks:

            task_to_add = {
                'id': task.id,
                'title': task.title,
                'url': Task.get_absolute_url_main(task),
                'status': task.status.title,
                'owner': '{} {}'.format(task.owner.last_name, task.owner.first_name),
                'executor': '{} {}'.format(task.executor.last_name, task.executor.first_name),
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

    # Получим задачи пользователя по умолчанию (для GET)
    def get_user_tasks(current_user_id):
        request_text = f"""            

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

    # ////////////////////////////////////////////////////////////
    # Получим обсуждение задачи

    def get_task_dispute(pk):

        image_extension = ['.jpg', '.JPG', '.jpeg', '.gif', '.bmp', '.png', '.heic']

        counter = 0
        dispute = []
        dispute_qs = Task_Dispute.objects.filter(task__pk=pk).order_by('created_at')
        for message_qs in dispute_qs:
            counter += 1

            is_image = False
            file_name = ''
            if message_qs.file:
                file_name = os.path.basename(message_qs.file.name)
                file_extension = os.path.splitext(file_name)[1]
                if file_extension in image_extension:
                    is_image = True

            if message_qs.in_reply_task_dispute == 0:
                dispute.append(
                    {'id': message_qs.id,
                     'user': get_user_name(message_qs.user),
                     'user_id': message_qs.user.id,
                     'content': message_qs.content,
                     'created_at': format_data(message_qs.created_at),
                     'in_reply': [],
                     'file': message_qs.file.url if message_qs.file else '',
                     'IsImage': is_image,
                     'FileName': file_name})
            else:
                # не нашел, как обратиться к конкретной строке, по-этому сделал цикл
                # нужно использовать element in list
                # Источник: https://egorovegor.ru/poisk-elementa-v-spiske-python
                for message in dispute:
                    if message['id'] == message_qs.in_reply_task_dispute:
                        in_reply = message['in_reply']
                        in_reply.append(
                            {'id': message_qs.id,
                             'user': get_user_name(message_qs.user),
                             'user_id': message_qs.user.id,
                             'in_reply_user': get_user_name(message_qs.in_reply_user),
                             'content': message_qs.content,
                             'created_at': format_data(message_qs.created_at),
                             'file': message_qs.file.url if message_qs.file else '',
                             'IsImage': is_image,
                             'FileName': file_name})

        return {'dispute': dispute, 'message_quantity': counter}

    def get_current_message_dict(message):

        image_extension = ['.jpg', '.jpeg', '.gif', '.bmp', '.png', '.heic']

        is_image = False
        file_name = ''
        if message.file:
            file_name = os.path.basename(message.file.name)
            file_extension = os.path.splitext(file_name)[1]
            if file_extension in image_extension:
                is_image = True

        current_message = {
            'id': message.id,
            'user': get_user_name(message.user),
            'user_id': message.user.id,
            'content': message.content,
            'created_at': format_data(message.created_at),
            'in_reply': [],
            'file': message.file.url if message.file else '',
            'IsImage': is_image,
            'FileName': file_name}

        if message.in_reply_task_dispute == 0:
            current_message['main_message'] = True
        else:
            current_message['main_message'] = False
            current_message['in_reply_user'] = get_user_name(message.in_reply_user)

        return current_message
