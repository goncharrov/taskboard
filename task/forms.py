from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from ckeditor_uploader.widgets import CKEditorUploadingWidget
from .models import Task, Workspace, Department, Project, User, Task_Status, Project_Status

User = get_user_model()


class UserLoginForm(AuthenticationForm):

    username = forms.CharField(label='Адрес эл. почты',
                               widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder':"name@example.com", "autocomplete": "off"}))
    password = forms.CharField(label='Пароль',
                                widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder':"Пароль"}))

class TaskNewForm(forms.Form):

    title = forms.CharField(max_length=150, widget=forms.TextInput(
        attrs={"class": "form-control form-control-sm", "autocomplete": "off"}))
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
        if department is not None:
            if department.workspace != workspace:
                raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
        return department


class TaskForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(TaskForm, self).__init__(*args, **kwargs)
        self.fields['department'].empty_label = ""
        self.fields['executor'].empty_label = ""
        self.fields['status'].empty_label = ""
        self.fields['project'].empty_label = ""
        user_qs = User.objects.all()
        self.fields['executor'].queryset = user_qs       

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

    def __init__(self, *args, **kwargs):
        super(ProjectForm, self).__init__(*args, **kwargs)
        self.fields['department'].empty_label = ""
        self.fields['status'].empty_label = ""       
    
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

    def __init__(self, *args, **kwargs):
        super(ProjectNewForm, self).__init__(*args, **kwargs)
        self.fields['workspace'].empty_label = ""
        self.fields['department'].empty_label = ""

    def clean_department(self):
        department = self.cleaned_data['department']
        workspace = self.cleaned_data['workspace']
        if department is not None:
            if department.workspace != workspace:
                raise ValidationError("Подразделение не относится к выбранному рабочему пространству")
        return department

    class Meta:
        model = Project
        fields = ['title','description','workspace','department']
        widgets = {
            'title': forms.TextInput(attrs={"class": "form-control form-control-sm", "autocomplete": "off"}),
            'description': CKEditorUploadingWidget(),
            'workspace': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
            'department': forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}),
        }

class MembersTaskForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), required=False, empty_label='', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_form-fields"}))

class SelectionTasksForm(forms.Form):
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.none(), required=False, empty_label='Рабочее пространство', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False,  empty_label='Подразделение', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    status = forms.ModelChoiceField(queryset=Task_Status.objects.all(), required=False, empty_label='Состояние', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    owner = forms.ModelChoiceField(queryset=User.objects.none(), required=False, empty_label='Автор', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    executor = forms.ModelChoiceField(queryset=User.objects.none(), required=False, empty_label='Исполнитель', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    project = forms.ModelChoiceField(queryset=Project.objects.none(), required=False, empty_label='Проект', widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))

class SelectionProjectsForm(forms.Form):
    workspace = forms.ModelChoiceField(queryset=Workspace.objects.none(), required=False,
                                       empty_label='Рабочее пространство', widget=forms.Select(
            attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    department = forms.ModelChoiceField(queryset=Department.objects.none(), required=False, empty_label='Подразделение',
                                        widget=forms.Select(
                                            attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    status = forms.ModelChoiceField(queryset=Project_Status.objects.all(), required=False, empty_label='Состояние',
                                    widget=forms.Select(
                                        attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    owner = forms.ModelChoiceField(queryset=User.objects.none(), required=False,
                                   empty_label='Автор',
                                   widget=forms.Select(attrs={"class": "form-select form-select-sm taskboard_sidebar_select"}))
    