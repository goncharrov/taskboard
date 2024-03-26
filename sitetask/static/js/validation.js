var url = window.location.href;

const save_new_form = document.querySelector('#save_new_form');
if (save_new_form != null) {
    save_new_form.addEventListener('click', run_form_validation);
}

const save_new_form_mobile = document.querySelector('#save_new_form_mobile');
if (save_new_form_mobile != null) {
    save_new_form_mobile.addEventListener('click', run_form_validation);
}

const title_input = document.querySelector("#id_title");
const workspace_input = document.querySelector("#id_workspace");
const department_input = document.querySelector("#id_department");
const executor_input = document.querySelector("#id_executor");
const status_input = document.querySelector("#id_status");
const project_input = document.querySelector("#id_project");

// Пример поиска класса через точку
const description_input = document.querySelector(".django-ckeditor-widget")

if (description_input != null) {
    // растягиваем description_input на всю ширину окна
    description_input.style.width = '100%';
}

function add_class(input_field, inner_text) {

    var input_validation = document.querySelector("#del_"+input_field.id);

    var field_value = input_field.value;
    if (field_value == '') {
        input_field.classList.add('taskboard_invalid');

        if (input_validation == null) {
            var new_validation = document.createElement("div");
            new_validation.className = "taskboard_invalid-feedback";
            new_validation.innerText = inner_text;
            new_validation.id = "del_" + input_field.id;
            // Пример добавления после текущего элемента
            input_field.after(new_validation);
        };

    } else {
        input_field.classList.remove('taskboard_invalid');
        if (input_validation != null) {
            // Пример удаления элемента
            input_validation.remove();
        };
    };
}

function run_form_validation() {

    if (title_input != null) {
        add_class(title_input,"Укажите наименование задачи");
    }
    if (workspace_input != null) {
        add_class(workspace_input,"Выберите рабочее пространство");
    }
    if (department_input != null) {
        add_class(department_input,"Выберите подразделение");
    }
    if (executor_input != null) {
        add_class(executor_input,"Выберите исполнителя");
    }
    if (status_input != null) {
        add_class(status_input,"Выберите исполнителя");
    }

}

// ---------------------------------------------------------
// Свяжем поля с выбранным рабочим пространством

if (workspace_input != null) {
    workspace_input.addEventListener('input', () => field_when_changing("workspace"));
}
department_input.addEventListener('input', () => field_when_changing("department"));

async function field_when_changing(field) {

//    var one_workspace = workspace_input.getElementsByTagName('option').length > 2 ? false : true;
//    && one_workspace == false

    if (field == "department") {
        if (workspace_input.hasAttribute("pk") == true) {
            var workspace_value = workspace_input.getAttribute("pk");
        } else {
            var workspace_value = workspace_input.value;
        }
    } else {
        var workspace_value = workspace_input.value;
    }

    if (workspace_value != "") {

        var selection = {};
        selection['workspace'] = workspace_value;
        selection['department'] = department_input.value;
        selection['name_field'] = field;

        var response = await fetch(url,{
        method: "GET",
        headers: {
            "Y-Requested-With": "XMLHttpRequest",
            "selection": JSON.stringify(selection),
        }
        })

        var data = await response.json();

        if (field == "workspace") {
            department_input.innerHTML = '';


            add_field_rows(department_input, data.departments);
            if (executor_input != null) {
                executor_input.innerHTML = '';
                add_field_rows(executor_input, data.users);
            }
            if (project_input != null) {
                project_input.innerHTML = '';
                add_field_rows(project_input, data.projects);
            }
        } else if (field == "department") {
            if (project_input != null) {
                project_input.innerHTML = '';
                add_field_rows(project_input, data.projects);
            }
        }

    } else {
        department_input.innerHTML = '';
        if (executor_input != null) {
            executor_input.innerHTML = '';
        }
        if (project_input != null) {
            project_input.innerHTML = '';
        }
    }

}

function add_field_rows(input,data) {
    add_empty_row(input);
    for (let item of data) {
        add_field_row(item, input);
    }
}

function add_field_row(item, item_input) {
    var NewRow = document.createElement("option");
    NewRow.value = item.id;
    NewRow.innerText = item.title;
    item_input.append(NewRow);
}

function add_empty_row(item_input) {
    var EmptyRow = document.createElement("option");
    EmptyRow.value = "";
    EmptyRow.setAttribute('selected','selected')
    item_input.append(EmptyRow);
}