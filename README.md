## Инициализация

```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

## Заполнить базу и первоначальные данные

```bash
./manage.py migrate
./manage.py create_default_data
```

## Краткое описание приложения

Приложение для управления задачами и проектами между группами пользователей. 
Базовая функциональность позволяет распределять пользователей по рабочим пространствам, назначать задачи и вести проекты в разрезе подразделений, группировать задачи по проектам.

Список задач

<image src="/.images/ExampleOfTaskList.jpg" width="800" height="425" alt="">

Создание новой задачи

<image src="/.images/ExampleOfCreatingNewTask.jpg" width="800" height="425" alt="">

Созданная задача

<image src="/.images/ExampleOfCreatedTask.jpg" width="800" height="425" alt="">

Обсуждение задачи

<image src="/.images/ExampleDiscussionTasks.jpg" width="800" height="425" alt="">

Список проектов

<image src="/.images/ExampleOfProjectList.jpg" width="800" height="425" alt="">

## Справочно
Для корректной работы текстового редактора "CKeditor" с файлами у пользователей в правах доступа должен быть включен "Статус персонала"

<image src="/.images/PersonnelStatus.jpg" width="800" height="425" alt="">
