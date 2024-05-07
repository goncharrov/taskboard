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

![Screen|800x425](https://ruproject.org/media/files/2024/05/07/ExampleOfTask_List.jpg)

Создание новой задачи

![Screen|800x425](https://ruproject.org/media/files/2024/05/07/ExampleOfCreatingNewTask.jpg)

Созданная задача

![Screen|800x425](https://ruproject.org/media/files/2024/05/07/ExampleOfCreatedTask.jpg)

Обсуждение задачи

![Screen|800x425](https://ruproject.org/media/files/2024/05/07/ExampleDiscussionTasks.jpg)

Список проектов

![Screen|800x425](https://ruproject.org/media/files/2024/05/07/ExampleOfProjectList.jpg)

## Справочно
Для корректной работы текстового редактора "CKeditor" с файлами у пользователей в правах доступа должен быть включен "Статус персонала"

![Screen|700x241](https://ruproject.org/media/files/2024/05/07/PersonnelStatus.jpg)
