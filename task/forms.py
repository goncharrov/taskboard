from django import forms
from .models import Task, Workspace, Department, Project, User, Task_Status, Project_Status
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from django.contrib.auth.forms import AuthenticationForm

User = get_user_model()
# print(User)

class UserLoginForm(AuthenticationForm):

    username = forms.CharField(label='Адрес эл. почты',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"name@example.com", "autocomplete": "off"}))
    password = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':"Пароль"}))

class TaskNewForm(forms.Form):

    title = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control form-control-sm", "autocomplete": "off"}))
    # description = forms.CharField(label='Описание', required=False, widget=forms.Textarea(
    #     attrs={"class": "form-control form-control-sm taskboard_form-fields", "rows": 4}))
    description = forms.CharField(label='Описание', required=False, widget=CKEditorUploadingWidget())
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.all(), empty_label='', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), empty_label='', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))
    executor = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='',
                                      widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, empty_label='',
                                     widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))
    finish_date = forms.DateField(label='Плановая дата выполнения', required=False, widget=forms.DateInput(
        attrs={"format": '%Y-%m-%d', "class": "form-control form-control-sm taskboard_form-fields", "type": 'date'}))

    def clean_department(self):
        department = self.cleaned_data['department']
        workspace = self.cleaned_data['workspace']
        if department != None:
            if department.workspace != workspace:
                raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
        return department

    # НЕЗАПОЛНЕННЫЕ ЗНАЧЕНИЯ НЕТ СМЫСЛА ВАЛИДИРОВАТЬ, ОНИ ПРОВЕРЯЮТСЯ ФОРМОЙ (required)

class TaskForm(forms.ModelForm):
    # переопределение __init__ формы
    # Super - вызывается родительский класс, а потом с помощью init переопределяю свойства
    # *args — array (неименнованные аргументы), **kwards — dictionary (именнованные аргументы)
    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        # self.fields['workspace'].empty_label = ""
        self.fields['department'].empty_label = ""
        self.fields['executor'].empty_label = ""
        self.fields['status'].empty_label = ""
        self.fields['project'].empty_label = ""

        # self.fields['workspace'].disabled = True

        # user_qs = User.objects.filter(is_superuser=False)
        user_qs = User.objects.all()
        self.fields['executor'].queryset = user_qs

        # Оставлю как пример фильтрации на форме
        # if 'initial' in kwargs:
        #     workspace = kwargs['initial']['workspace']
        #     if workspace is not None:
        #         department_qs = Department.objects.filter(workspace__pk=workspace.pk)
        #         self.fields['department'].queryset = department_qs

    # def clean_department(self):
    #     print(self.cleaned_data)
    #     department = self.cleaned_data['department']
    #     workspace = self.cleaned_data['workspace']
    #     if department != None:
    #         if department.workspace != workspace:
    #             raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
    #     return department

    class Meta:
        model = Task
        fields = ['department','executor','status','project','finish_date']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control form-control-sm", "autocomplete": "off"}),
            'description': forms.Textarea(attrs={"class": "form-control form-control-sm taskboard_form-fields", "rows": 4}),
            'workspace': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'department': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'owner': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'executor': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'status': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'project': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'created_at': forms.DateInput(attrs={"class": "form-control form-control-sm taskboard_form-fields","type": 'date',},format="%Y-%m-%d"),
            'finish_date': forms.DateInput(attrs={"class": "form-control form-control-sm taskboard_form-fields","type": 'date',},format="%Y-%m-%d"),
        }

class TaskFormExecutor(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(TaskFormExecutor, self).__init__(*args, **kwargs)
        self.fields['status'].empty_label = ""

    class Meta:
        model = Task
        fields = ['status','finish_date']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control form-control-sm", "autocomplete": "off"}),
            'description': forms.Textarea(attrs={"class": "form-control form-control-sm taskboard_form-fields", "rows": 4}),
            'workspace': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'department': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'owner': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'executor': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'status': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'project': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'created_at': forms.DateInput(attrs={"class": "form-control form-control-sm taskboard_form-fields","type": 'date',},format="%Y-%m-%d"),
            'finish_date': forms.DateInput(attrs={"class": "form-control form-control-sm taskboard_form-fields","type": 'date',},format="%Y-%m-%d"),
        }

class ProjectForm(forms.ModelForm):

    # В fields нужно указывать только те поля, которые нужно будет перезаписывать
    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        # self.fields['workspace'].empty_label = ""
        self.fields['department'].empty_label = ""
        self.fields['status'].empty_label = ""

        # self.fields['workspace'].disabled = True

        # if 'initial' in kwargs:
        #     workspace = kwargs['initial']['workspace']
        #     if workspace is not None:
        #         department_qs = Department.objects.filter(workspace__pk=workspace.pk)
        #         self.fields['department'].queryset = department_qs

    # def clean_department(self):
    #     department = self.cleaned_data['department']
    #     workspace = self.cleaned_data['workspace']
    #     if department != None:
    #         if department.workspace != workspace:
    #             raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
    #     return department

    class Meta:
        model = Project
        fields = ['department','status', 'finish_date']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control form-control-sm", "autocomplete": "off"}),
            'description': forms.Textarea(attrs={"class": "form-control form-control-sm taskboard_form-fields", "rows": 4}),
            'workspace': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'department': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'status': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'finish_date': forms.DateInput(attrs={"class": "form-control form-control-sm taskboard_form-fields", "type": 'date', }, format="%Y-%m-%d"),
        }

class ProjectNewForm(forms.ModelForm):

    # В fields нужно указывать только те поля, которые нужно будет перезаписывать
    def __init__(self, *args, **kwargs):
        super(ProjectNewForm, self).__init__(*args, **kwargs)
        self.fields['workspace'].empty_label = ""
        self.fields['department'].empty_label = ""

    def clean_department(self):
        department = self.cleaned_data['department']
        workspace = self.cleaned_data['workspace']
        if department != None:
            if department.workspace != workspace:
                raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
        return department

    class Meta:
        model = Project
        fields = ['title','description','workspace','department']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control form-control-sm", "autocomplete": "off"}),
            # 'description': forms.Textarea(attrs={"class": "form-control form-control-sm taskboard_form-fields", "rows": 4}),
            'description': CKEditorUploadingWidget(),
            'workspace': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'department': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
        }

class MembersTaskForm(forms.Form):

    # НЕ привязываем к модели, так как  нужно вывести просто таблицу пользователей
    # queryset = User.objects.filter(is_superuser=False)
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label='', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))

class SelectionTasksForm(forms.Form):
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.all(), required=False, empty_label='Рабочее пространство', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False,  empty_label='Подразделение', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    status = forms.ModelChoiceField(queryset=Task_Status.objects.all(), required=False, empty_label='Состояние', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    owner = forms.ModelChoiceField(queryset=User.objects.filter(is_superuser=False), required=False, empty_label='Автор', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    executor = forms.ModelChoiceField(queryset=User.objects.filter(is_superuser=False), required=False, empty_label='Исполнитель', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    project = forms.ModelChoiceField(queryset=Project.objects.all(), required=False, empty_label='Проект', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))

class SelectionProjectsForm(forms.Form):
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.all(), required=False,
                                       empty_label='Рабочее пространство', widget=forms.Select(
            attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    department = forms.ModelChoiceField(queryset=Department.objects.all(), required=False, empty_label='Подразделение',
                                        widget=forms.Select(
                                            attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    status = forms.ModelChoiceField(queryset=Project_Status.objects.all(), required=False, empty_label='Состояние',
                                    widget=forms.Select(
                                        attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    owner = forms.ModelChoiceField(queryset=User.objects.filter(is_superuser=False), required=False,
                                   empty_label='Автор',
                                   widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))