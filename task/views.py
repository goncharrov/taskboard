import json
import datetime
import locale
from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import ListView, DetailView, CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.http import HttpResponseRedirect, JsonResponse
from django.contrib.auth import login, logout

import task.forms as task_forms

from task.logic import task_filters, project_filters, task_disputes, form_selections, user_rights
from task.models import Department, Task, Project, User, Task_Status, Project_Status, Task_Dispute, Task_Members, Project_Members, User_Rights, Workspace

locale.setlocale(locale.LC_ALL, 'ru_RU.UTF-8')


def user_login(request):

    if request.user.is_authenticated is True:
        return redirect('tasks')

    if request.method == 'POST':
        form = task_forms.UserLoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request,user)
            return redirect('tasks')
    else:
        form = task_forms.UserLoginForm()

    return render(request, 'task/login.html', {"form": form})

def user_logout(request):
    logout(request)
    return redirect('login')

# Функции views
class GetProjects(ListView):
    model = Project
    template_name = 'task/project_list.html'
    context_object_name = 'projects'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated is False:
            return redirect('login')

        projects: list = []
        user_right = User_Rights.objects.get(user=request.user).role
        filters_data: dict = project_filters.create_project_filters_dict(request.user.id)

        is_ajax: bool = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

        if is_ajax:

            if request.method == 'GET':

                # Быстрые отборы
                quick_selection = request.headers.get('quick-selection')
                quick_selection_data = json.loads(quick_selection)

                # Быстрые отборы (приведем значения к булево)
                quick_selection_data['check_1_my_projects'] = False if quick_selection_data['check_1_my_projects'] == "off" else True
                quick_selection_data['check_2_projects_participation'] = False if quick_selection_data['check_2_projects_participation'] == "off" else True

                # Селекторы
                selection = request.headers.get('selection')
                selection_data = json.loads(selection)

                filters = {'quick_selection': quick_selection_data, 'selection_data': selection_data, 'current_user': request.user.id}
                filters_data = project_filters.get_form_project_filters(filters, filters_data)

                # Если включен только второй чек, а первый выключен, то запрос по проектам не формируем
                if not (quick_selection_data['check_1_my_projects'] is False and quick_selection_data['check_2_projects_participation'] is True):
                    if user_right.is_full:
                        projects = project_filters.get_user_projects_and_tasks_full_rights(projects, filters_data)
                    else:
                        projects = project_filters.get_user_projects_and_tasks(projects, filters_data)

                if quick_selection_data['check_2_projects_participation'] is True:
                    # Запрос по участникам проекта
                    projects = project_filters.get_project_members(projects, filters_data, user_right)

                projects.sort(key=lambda dictionary: dictionary['created_at'], reverse=True)

                return JsonResponse({'context': projects})

        else:

            selection_form = task_forms.SelectionProjectsForm()

            # Заполним данные селекторов
            workspace_list = form_selections.get_user_workspaces_list(request.user)
            workspace_qs = Workspace.objects.filter(pk__in=workspace_list)
            selection_form.fields['workspace'].queryset = workspace_qs

            department_qs = Department.objects.filter(workspace__pk__in=workspace_list)
            selection_form.fields['department'].queryset = department_qs

            users_qs = form_selections.get_users_by_workspace(workspace_list)
            selection_form.fields['owner'].queryset = users_qs            

            # Заполним список проектов
            if user_right.is_full:
                projects = project_filters.get_user_projects_and_tasks_full_rights(projects, filters_data)
            else:
                projects = project_filters.get_user_projects_and_tasks(projects, filters_data)

            projects.sort(key=lambda dictionary: dictionary['created_at'], reverse=True)

            context = {'selection': selection_form, 'projects': projects}

            return render(request, self.template_name, context)

def get_project_main(request, pk):

    if request.user.is_authenticated is False:
        return redirect('login')

    project_item = get_object_or_404(Project, pk=pk)
    current_user = request.user

    # Проверим доступ к проекту
    have_access_to_project = user_rights.check_permissions_on_project(project_item, request.user)
    if have_access_to_project['access'] is not True:
        return render(request, 'task/blank_main.html', have_access_to_project)

    # Получим права доступа к реквизитам формы
    input_right = user_rights.get_input_right('project', project_item, current_user.id)

    # Если доступ есть, работаем с проектом
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:

        if request.method == 'GET':

            members: list = []
            members_qs = Project_Members.objects.filter(project=pk).order_by('pk')
            for item in members_qs:
                members.append({'id': item.id, 'user': f"{item.user.last_name} {item.user.first_name}"})

            return JsonResponse({'context': members})

        if request.method == 'POST':

            data = json.load(request)
            user_id = data.get('user')

            project = Project.objects.get(pk=pk)
            member = User.objects.get(pk=user_id)

            if member == project_item.owner:
                return JsonResponse({'status': 'User is already owner!'}, safe=False)
            else:
                members = Project_Members.objects.filter(project=project, user=member)
                if members.count() == 0:
                    Project_Members.objects.create(project=project, user=member)
                    return JsonResponse({'status': 'User added!'}, safe=False)
                else:
                    return JsonResponse({'status': 'The user is already a member!'}, safe=False)

        if request.method == 'DELETE':
            data = json.load(request)
            project_member_id = data.get('member_id')
            member = Project_Members.objects.get(pk=project_member_id)
            member.delete()

            return JsonResponse({'status': 'User removed!'}, safe=False)

        return JsonResponse({'status': 'Invalid request'}, status=400)

    else:

        if request.method == 'POST':

            status_closed = Project_Status.objects.get(pk=2)

            if project_item.status == status_closed:
                return redirect(project_item.get_absolute_url_main())

            form_project = task_forms.ProjectForm(request.POST)
            form_members = task_forms.MembersTaskForm(request.POST)

            if form_project.is_valid():

                is_error = False

                if form_project.cleaned_data['status'] == status_closed:
                    if Task.objects.filter(project=project_item, status__id__in=[1, 2, 4]).exists():
                        messages.error(request, 'По проекту остались незакрытые задачи!')
                        is_error = True

                if form_project.cleaned_data['department'] != project_item.department:
                    if Task.objects.filter(project=project_item, department=project_item.department).exists():
                        messages.error(request, f'По проекту есть задачи с подразделением "{project_item.department.title}" !')
                        is_error = True

                if not is_error:
                    project = Project.objects.get(pk=pk)
                    project.department = form_project.cleaned_data['department']
                    project.status = form_project.cleaned_data['status']
                    project.finish_date = form_project.cleaned_data['finish_date']
                    if form_project.cleaned_data['status'] == status_closed:
                        project.clousing_date = datetime.date.today()
                    project.save()

                return redirect(project_item.get_absolute_url_main())

        if request.method == 'GET':
            form_project = task_forms.ProjectForm(initial={
                'title': project_item.title,
                'description': project_item.description,
                'workspace': project_item.workspace,
                'department': project_item.department,
                'owner': project_item.owner,
                'status': project_item.status,
                'created_at': project_item.created_at,
                'finish_date': project_item.finish_date,
                'clousing_date': project_item.clousing_date,
            })

            form_project.fields['department'].queryset = Department.objects.filter(workspace__pk=project_item.workspace.id)

            # Форма участников проекта
            form_members = task_forms.MembersTaskForm(initial={
                'user': None,
            })
            users_qs = form_selections.get_users_by_workspace([project_item.workspace.id, ])
            form_members.fields['user'].queryset = users_qs

        members = Project_Members.objects.filter(project__pk=pk)

        return render(request, 'task/project_main.html', {'form': form_project, 'project_item': project_item, 'form_members': form_members, 'members': members, 'input_right': input_right})

class GetProjectTasks(DetailView):
    model = Project
    template_name = 'task/project_tasks.html'
    context_object_name = 'project_item'

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated is False:
            return redirect('login')

        current_project = Project.objects.get(pk=self.kwargs['pk'])

        have_access_to_project = user_rights.check_permissions_on_project(current_project, request.user)
        if have_access_to_project['access'] is not True:
            return render(request, 'task/blank_main.html', have_access_to_project)

        user_right = User_Rights.objects.get(user=request.user).role
        if user_right.is_full:
            tasks_qs = Task.objects.filter(project=current_project)
        else:
            tasks_qs = project_filters.get_user_project_tasks(current_project.id, self.request.user.id)

        tasks_table = task_filters.get_tasks_seriales_data(tasks=[], tasks_qs=tasks_qs, type_table="task", current_user_id=request.user.id)

        context = {}
        context['project_item'] = current_project
        context['project_tasks'] = tasks_table

        return render(request, self.template_name, context)

class AddNewProject(CreateView):

    model = Project
    form_class = task_forms.ProjectNewForm
    template_name = 'task/new_project.html'

    def form_valid(self, form):
        self.object = form.save(False)
        self.object.owner = self.request.user
        self.object.status = Project_Status.objects.get(pk=1)
        self.object.title = self.object.title.capitalize()
        self.object.save()

        return HttpResponseRedirect(self.get_success_url())

    def get_success_url(self):
        return reverse_lazy('view_project_main', kwargs={'pk': self.object.pk})

    def get(self, request, *args, **kwargs):

        if request.user.is_authenticated is False:
            return redirect('login')

        is_ajax = request.headers.get('Y-Requested-With') == 'XMLHttpRequest'

        if is_ajax:

            selection = request.headers.get('selection')
            selection_data = json.loads(selection)

            departments = []
            if selection_data['name_field'] == "workspace":

                department_qs = Department.objects.filter(workspace__pk=selection_data['workspace'])
                for item_department in department_qs:
                    departments.append({'id': item_department.id,
                                        'title': f"{item_department.workspace.title} {item_department.title}"})

            return JsonResponse({'departments': departments})

        else:

            form = task_forms.ProjectNewForm()
            # Установим фильтры на поля формы
            workspace_list = form_selections.get_user_workspaces_list(request.user)
            form.fields['workspace'].queryset = Workspace.objects.filter(pk__in=workspace_list)
            form.fields['department'].queryset = Department.objects.filter(workspace__pk__in=workspace_list)

            context = {'form': form}
            return render(request, self.template_name, context)

def get_tasks(request):

    if request.user.is_authenticated is False:
        return redirect('login')

    tasks: list = []
    user_right = User_Rights.objects.get(user=request.user).role

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:

        if request.method == 'GET':

            # Быстрые отборы
            quick_selection = request.headers.get('quick-selection')
            quick_selection_data = json.loads(quick_selection)

            # Быстрые отборы (приведем значения к булево)
            quick_selection_data['check_1_my_tasks'] = False if quick_selection_data['check_1_my_tasks'] == "off" else True
            quick_selection_data['check_2_tasks_to_complete'] = False if quick_selection_data['check_2_tasks_to_complete'] == "off" else True
            quick_selection_data['check_3_tasks_participation'] = False if quick_selection_data['check_3_tasks_participation'] == "off" else True

            # Селекторы
            selection = request.headers.get('selection')
            selection_data = json.loads(selection)

            filters = {'quick_selection': quick_selection_data, 'selection_data': selection_data, 'current_user': request.user.id}
            filters_data = task_filters.get_form_task_filters(filters)

            # Если включен только третий чек, а остальные выключены, то запрос по задачам не формируем
            if not ((quick_selection_data['check_1_my_tasks'] is False and quick_selection_data['check_2_tasks_to_complete'] is False) and quick_selection_data['check_3_tasks_participation'] is True):
                tasks_qs = task_filters.get_user_tasks_selection(filters_data, user_right)
                tasks = task_filters.get_tasks_seriales_data(tasks, tasks_qs, "task", request.user.id)

            # Добавляем участников задачи
            if quick_selection_data['check_3_tasks_participation'] is True:
                tasks_members_qs = task_filters.get_task_members(filters_data)
                tasks = task_filters.get_tasks_seriales_data(tasks, tasks_members_qs, "task_members", request.user.id)

            tasks.sort(key=lambda dictionary: dictionary['created_at'], reverse=True)

            return JsonResponse({'context': tasks})

    else:

        selection_form = task_forms.SelectionTasksForm()

        # Заполним данные селекторов
        workspace_list = form_selections.get_user_workspaces_list(request.user)
        workspace_qs = Workspace.objects.filter(pk__in=workspace_list)
        selection_form.fields['workspace'].queryset = workspace_qs

        department_qs = Department.objects.filter(workspace__pk__in=workspace_list)
        selection_form.fields['department'].queryset = department_qs

        users_qs = form_selections.get_users_by_workspace(workspace_list)
        selection_form.fields['owner'].queryset = users_qs
        selection_form.fields['executor'].queryset = users_qs
        selection_form.fields['project'].queryset = form_selections.get_user_projects(request.user.id, None)

        # Заполним список задач
        if user_right.is_full:
            all_tasks_qs = Task.objects.all().order_by('-created_at')
            tasks_table = task_filters.get_tasks_seriales_data(tasks, all_tasks_qs, "task", request.user.id)
        else:
            all_tasks_qs = task_filters.get_user_tasks(request.user.id)
            tasks_table = task_filters.get_tasks_seriales_data(tasks, all_tasks_qs, "task", request.user.id)
            tasks_table.sort(key=lambda dictionary: dictionary['created_at'], reverse=True)

        context = {'selection': selection_form, 'tasks': tasks_table}

        return render(request, 'task/task_list.html', context)

def add_new_task(request):

    if request.user.is_authenticated is False:
        return redirect('login')

    is_ajax = request.headers.get('Y-Requested-With') == 'XMLHttpRequest'

    if is_ajax:

        if request.method == 'GET':

            selection = request.headers.get('selection')
            selection_data = json.loads(selection)

            departments = []
            if selection_data['name_field'] == "workspace":

                department_qs = Department.objects.filter(workspace__pk=selection_data['workspace'])
                for item_department in department_qs:
                    departments.append({'id': item_department.id,
                                        'title': f"{item_department.workspace.title} {item_department.title}"})

            users = []
            users_qs = form_selections.get_users_by_workspace(list(selection_data['workspace']))
            for item_user in users_qs:
                users.append({'id': item_user.id, 'title': f"{item_user.last_name} {item_user.first_name}"})

            projects = []
            if selection_data['workspace'] != "" and selection_data['department'] != "":

                filters = {'workspace': selection_data['workspace'], 'department': selection_data['department']}
                projects_qs = form_selections.get_user_projects(request.user.id, filters)
                for item_project in projects_qs:
                    projects.append({'id': item_project.id, 'title': item_project.title})

            return JsonResponse({'departments': departments, 'users': users, 'projects': projects})

    else:

        if request.method == 'POST':

            form = task_forms.TaskNewForm(request.POST)

            owner = request.user
            status = Task_Status.objects.get(pk=1)

            if form.is_valid():

                title = form.cleaned_data['title']
                description = form.cleaned_data['description']
                workspace = form.cleaned_data['workspace']
                department = form.cleaned_data['department']
                executor = form.cleaned_data['executor']
                project = form.cleaned_data['project']
                finish_date = form.cleaned_data['finish_date']

                title = title.capitalize()

                task = Task.objects.create(title=title, description=description, workspace=workspace, department=department, executor=executor, project=project, owner=owner, status=status, finish_date=finish_date)

                return redirect(task.get_absolute_url_main())

        else:
            form = task_forms.TaskNewForm()

            # Установим фильтры на поля формы
            workspace_list = form_selections.get_user_workspaces_list(request.user)
            form.fields['workspace'].queryset = Workspace.objects.filter(pk__in=workspace_list)
            form.fields['department'].queryset = Department.objects.filter(workspace__pk__in=workspace_list)
            if len(workspace_list) == 1:
                form.fields['executor'].queryset = form_selections.get_users_by_workspace(workspace_list)
            else:
                form.fields['executor'].queryset = User.objects.filter(pk=0)
            form.fields['project'].queryset = Project.objects.filter(pk=0)

        return render(request, 'task/new_task.html', {'form': form})

def get_task_main(request, pk):

    if request.user.is_authenticated is False:
        return redirect('login')

    task_item = get_object_or_404(Task, pk=pk)
    current_user = request.user

    # Проверим доступ к задаче
    have_access_to_task = user_rights.check_permissions_on_task(task_item, request.user)
    if have_access_to_task['access'] is not True:
        return render(request, 'task/blank_main.html', have_access_to_task)

    # Посчитаем количество непрочитанных сообщений
    related_task_message = task_item.related_task_message.filter(user=request.user).first()
    if related_task_message is None:
        new_messages = 0
    else:
        new_messages = related_task_message.new_messages

    # Получим права доступа к реквизитам формы
    input_right = user_rights.get_input_right('task', task_item, current_user.id)

    # Если доступ есть, работаем с задачей
    is_ajax_members = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
    is_ajax_fields = request.headers.get('Y-Requested-With') == 'XMLHttpRequest'

    is_ajax = is_ajax_members is True or is_ajax_fields is True

    if is_ajax:

        if is_ajax_members:

            # Получение списка участника проекта
            if request.method == 'GET':

                members = []
                members_qs = Task_Members.objects.filter(task__pk=pk).order_by('pk')
                for item in members_qs:
                    members.append({'id': item.id, 'user': f"{item.user.last_name} {item.user.first_name}"})

                return JsonResponse({'context': members})

            # Запись участника проекта
            if request.method == 'POST':

                if request.headers.get('type-operation') == "add_member":

                    data = json.load(request)
                    user_id = data.get('user')
                    member = User.objects.get(pk=user_id)

                    if member == task_item.owner:
                        return JsonResponse({'status': 'User is already owner!'}, safe=False)
                    elif member == task_item.executor:
                        return JsonResponse({'status': 'User is already executor!'}, safe=False)
                    else:
                        members = Task_Members.objects.filter(task=task_item, user=member)
                        if members.count() == 0:
                            Task_Members.objects.create(task=task_item, user=member)
                            return JsonResponse({'status': 'User added!'}, safe=False)
                        else:
                            return JsonResponse({'status': 'User is already member!'}, safe=False)
                else:
                    if task_item.project:
                        members_qs = Project_Members.objects.filter(project=task_item.project)
                        for item_member in members_qs:
                            members = Task_Members.objects.filter(task=task_item, user=item_member.user)
                            if members.count() == 0:
                                Task_Members.objects.create(task=task_item, user=item_member.user)
                        return JsonResponse({'status': 'Users added!'}, safe=False)
                    else:
                        return JsonResponse({'status': 'No project in task!'}, safe=False)
                    return JsonResponse({'status': 'Data loading error!'}, safe=False)

            # Удаление участника проекта
            if request.method == 'DELETE':
                data = json.load(request)
                task_member_id = data.get('member_id')
                member = Task_Members.objects.get(pk=task_member_id)
                member.delete()

                return JsonResponse({'status': 'User removed!'}, safe=False)

            return JsonResponse({'status': 'Invalid request'}, status=400)

        if is_ajax_fields:

            if request.method == 'GET':

                selection = request.headers.get('selection')
                selection_data = json.loads(selection)

                projects = []
                if selection_data['workspace'] != "" and selection_data['department'] != "":

                    filters = {'workspace': selection_data['workspace'], 'department': selection_data['department']}
                    projects_qs = form_selections.get_user_projects(request.user.id, filters)
                    for item_project in projects_qs:
                        projects.append({'id': item_project.id, 'title': item_project.title})

                return JsonResponse({'departments': [], 'users': [], 'projects': projects})

    else:

        if request.method == 'POST':

            status_closed = Task_Status.objects.get(pk=3)
            status_cancel = Task_Status.objects.get(pk=5)

            if task_item.status.id == status_closed:
                return redirect(task_item.get_absolute_url_main())

            if task_item.owner.id == current_user.id:
                form_task = task_forms.TaskForm(request.POST)
            else:
                form_task = task_forms.TaskFormExecutor(request.POST)

            form_members = task_forms.MembersTaskForm(request.POST)

            if form_task.is_valid():
                task = Task.objects.get(pk=pk)
                if task_item.owner.id == current_user.id:
                    task.department = form_task.cleaned_data['department']
                    task.executor = form_task.cleaned_data['executor']
                    task.project = form_task.cleaned_data['project']
                task.status = form_task.cleaned_data['status']
                task.finish_date = form_task.cleaned_data['finish_date']
                if form_task.cleaned_data['status'] == status_closed \
                        or form_task.cleaned_data['status'] == status_cancel:
                    task.clousing_date = datetime.date.today()
                task.save()

                return redirect(task_item.get_absolute_url_main())
        else:
            # Передаем данные в форму
            form_task = task_forms.TaskForm(initial={
                'title': task_item.title,
                'description': task_item.description,
                'workspace': task_item.workspace,
                'department': task_item.department,
                'owner': task_item.owner,
                'executor': task_item.executor,
                'project': task_item.project,
                'status': task_item.status,
                'created_at': task_item.created_at,
                'finish_date': task_item.finish_date,
                'clousing_date': task_item.clousing_date,
            })

            # Установим фильтры на поля формы

            available_users = form_selections.get_users_by_workspace([task_item.workspace.id,])

            form_task.fields['department'].queryset = Department.objects.filter(workspace__pk=task_item.workspace.id)
            form_task.fields['executor'].queryset = available_users

            filters = {'workspace': task_item.workspace.id, 'department': task_item.department.id}
            form_task.fields['project'].queryset = form_selections.get_user_projects(task_item.owner.id, filters)

            # Форма участников проекта
            form_members = task_forms.MembersTaskForm(initial={
                'user': None,
            })
            users_qs = available_users
            form_members.fields['user'].queryset = users_qs

        members = Task_Members.objects.filter(task__pk=pk)

        return render(request, 'task/task_main.html', {'form': form_task,'task_item': task_item, 'form_members': form_members, 'members': members, 'new_messages': new_messages, 'user_id': current_user.id, 'input_right': input_right})

def get_task_chat_def(request, pk):

    if request.user.is_authenticated is False:
        return redirect('login')

    # Проверим доступ к задаче
    current_task = Task.objects.get(pk=pk)
    current_user = request.user

    have_access_to_task = user_rights.check_permissions_on_task(current_task, current_user)
    if have_access_to_task['access'] is not True:
        return render(request, 'task/blank_main.html', have_access_to_task)

    is_task_closed = True if current_task.status.id == 3 or current_task.status.id == 5 else False

    # Если доступ есть, работаем с задачей

    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'

    if is_ajax:

        if request.method == 'GET':

            result = task_disputes.get_task_dispute(pk)
            return JsonResponse({'context': result['dispute']})

        if request.method == 'POST':

            reply_user = None
            main_message_id = 0
            file = None

            if request.headers.get('type-message') == "send-file":
                content = request.POST.get('caption')
                file = request.FILES.get('file')
                message_id = request.POST.get('id')
            else:
                data = json.load(request)
                content = data.get('message').strip()
                message_id = data.get('id')

            if int(message_id) > 0:
                reply_message = Task_Dispute.objects.get(pk=message_id)
                reply_user = reply_message.user
                if reply_message.in_reply_task_dispute > 0:
                    main_message_id = reply_message.in_reply_task_dispute
                else:
                    main_message_id = message_id

            new_message = Task_Dispute.objects.create(task=current_task, user=current_user, content=content, in_reply_task_dispute=main_message_id, in_reply_user=reply_user, file=file)

            new_message_dict = task_disputes.get_current_message_dict(new_message)

            task_filters.add_task_count_messages(current_task, current_user)

            return JsonResponse({'status': 'Message added!', 'message': new_message_dict, 'user_id': current_user.id}, safe=False)

        return JsonResponse({'status': 'Invalid request'}, status=400)

    else:

        task_item = get_object_or_404(Task, pk=pk)
        result = task_disputes.get_task_dispute(pk)

        task_filters.clean_task_count_messages(current_task, request.user)

        return render(request, 'task/task_chat.html', {'dispute': result['dispute'], 'task_item': task_item, 'message_quantity': result['message_quantity'], 'user_id': current_user.id, 'is_task_closed': is_task_closed})
    