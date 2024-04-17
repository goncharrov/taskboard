import random
from task.models import Task_Members, User_Rights, Project_Members, Unauthorized_Access_Attempts


def check_permissions_on_task(current_task, current_user) -> dict:

    x = random.randint(1, 5)
    if x == 1:
        image_name = 'img/jack1.gif'
    else:
        image_name = f'img/jack{x}.jpeg'

    user_right = User_Rights.objects.get(user=current_user).role
    if user_right.is_full:
        return {'image_name': image_name, 'access': True}

    have_access_to_task = False
    if current_task.owner == current_user or current_task.executor == current_user:
        have_access_to_task = True

    is_member_qs = Task_Members.objects.filter(task=current_task, user=current_user)
    if is_member_qs.count() > 0:
        have_access_to_task = True

    if have_access_to_task is False:
        Unauthorized_Access_Attempts.objects.create(url=current_task.get_absolute_url_main(), user=current_user)

    return {'image_name': image_name, 'access': have_access_to_task}

def check_permissions_on_project(current_project, current_user) -> dict:

    x = random.randint(1, 5)
    if x == 1:
        image_name = 'img/jack1.gif'
    else:
        image_name = f'img/jack{x}.jpeg'

    user_right = User_Rights.objects.get(user=current_user).role
    if user_right.is_full:
        return {'image_name': image_name, 'access': True}

    have_access_to_project = False
    if current_project.owner == current_user:
        have_access_to_project = True

    is_member_qs = Project_Members.objects.filter(project=current_project, user=current_user)
    if is_member_qs.count() > 0:
        have_access_to_project = True

    if have_access_to_project is False:
        Unauthorized_Access_Attempts.objects.create(url=current_project.get_absolute_url_main(), user=current_user)

    return {'image_name': image_name, 'access': have_access_to_project}

def get_input_right(type_form, item, user_id) -> dict:

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
