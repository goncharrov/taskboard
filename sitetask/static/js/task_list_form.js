var url = window.location.href;

document.querySelector('#id_apply_selection').addEventListener('click', get_list);
document.querySelector('#id_apply_active').addEventListener('click', () => get_active(false));
document.querySelector('#id_apply_completed').addEventListener('click', () => get_completed(false));

var TasksList = document.querySelector("#tasks_list");

// Поля отбора
const SelectionWorkspace = document.querySelector("#id_workspace");
const SelectionDepartment = document.querySelector("#id_department");
const SelectionStatus = document.querySelector("#id_status");
const SelectionOwner = document.querySelector("#id_owner");
const SelectionExecutor = document.querySelector("#id_executor");
const SelectionProject = document.querySelector("#id_project");

// Быстрые отборы

var quick_selection = {
    check_1: "off",
    check_2: "off",
    check_3: "off",
    is_active: false,
    is_completed: false,
    period: "clean_period",
};

// Отбор по периодам

document.querySelector("#id_button_week").addEventListener('click', () =>  change_period("week","Неделя"));
document.querySelector("#id_button_month").addEventListener('click', () =>  change_period("month","Месяц"));
document.querySelector("#id_button_quarter").addEventListener('click', () =>  change_period("quarter","Квартал"));
document.querySelector("#id_button_year").addEventListener('click', () =>  change_period("year","Год"));
document.querySelector("#id_button_clean_period").addEventListener('click', () =>  change_period("clean_period","Период"));

function change_period(period,period_perform) {
    ButtonPeriod = document.querySelector("#id_button_period");
    ButtonPeriodText = document.querySelector("#id_button_period_text");
    ButtonPeriodText.innerText = period_perform;
    change_color_button_period(ButtonPeriod, period);
    quick_selection['period'] = period;
    get_list();
}

function change_color_button_period(button, period) {
//    console.log(button.style);
    if (period == "clean_period") {
        button.style.borderColor = "";
        button.style.borderWidth = "";
    } else {
        button.style.borderColor = "#86b7fe";
        button.style.borderWidth = "2.5px";
    }
}

// Стили кнопок

// При обновлении страницы

SelectionWorkspace.addEventListener('click', () =>  change_color_selection(SelectionWorkspace));
SelectionDepartment.addEventListener('click', () =>  change_color_selection(SelectionDepartment));
SelectionStatus.addEventListener('click', () =>  change_color_selection(SelectionStatus));
SelectionOwner.addEventListener('click', () =>  change_color_selection(SelectionOwner));
SelectionExecutor.addEventListener('click', () =>  change_color_selection(SelectionExecutor));
SelectionProject.addEventListener('click', () =>  change_color_selection(SelectionProject));

function change_color_selection(input_selection) {
//    console.log(input_selection.style);
    if (input_selection.value == "") {
        input_selection.style.borderColor = "";
        input_selection.style.borderWidth = "";
    } else {
        input_selection.style.borderColor = "#86b7fe";
        input_selection.style.borderWidth = "2.5px";
    }
}

function get_check_1(id, value) {
    quick_selection['check_1'] = value;
    if (value == "on") {
        SelectionOwner.value = "";
        SelectionOwner.setAttribute('disabled', true);
    } else {
        SelectionOwner.removeAttribute('disabled');
    };
    change_color_selection(SelectionOwner);
    get_list();
}

function get_check_2(id, value) {
     quick_selection['check_2'] = value;
     if (value == "on") {
        SelectionExecutor.value = "";
        SelectionExecutor.disabled = true;
    } else {
        SelectionExecutor.disabled = false;
    };
    change_color_selection(SelectionExecutor);
    get_list();
}

function get_check_3(id, value) {
    quick_selection['check_3'] = value;
    get_list();
}

// Обработка группы кнопок

function manage_selection_status() {

    if (quick_selection['is_active'] == true || quick_selection['is_completed'] == true) {
        SelectionStatus.disabled = true;
        SelectionStatus.value = "";
    }   else {
        SelectionStatus.disabled = false;
    };
    change_color_selection(SelectionStatus);

}

function get_active(is_mobile) {

    if (is_mobile == true) {
        var button_active = document.querySelector('#id_apply_active_mobile');
        var button_completed = document.querySelector('#id_apply_completed_mobile');
    } else {
        var button_active = document.querySelector('#id_apply_active');
        var button_completed = document.querySelector('#id_apply_completed');
    }

    if (button_active.classList.contains("active") == true) {
        button_active.classList.remove("active");
        quick_selection['is_active'] = false;
    } else {
        button_active.classList.add("active");
        quick_selection['is_active'] = true;
        if (button_completed.classList.contains("active") == true) {
            button_completed.classList.remove("active");
            quick_selection['is_completed'] = false;
        };
    };

    manage_selection_status();
    get_list();
}

function get_completed(is_mobile) {

   if (is_mobile == true) {
        var button_active = document.querySelector('#id_apply_active_mobile');
        var button_completed = document.querySelector('#id_apply_completed_mobile');
    } else {
        var button_active = document.querySelector('#id_apply_active');
        var button_completed = document.querySelector('#id_apply_completed');
    }

    if (button_completed.classList.contains("active") == true) {
        button_completed.classList.remove("active");
        quick_selection['is_completed'] = false;
    } else {
        button_completed.classList.add("active");
        quick_selection['is_completed'] = true;
        if (button_active.classList.contains("active") == true) {
            button_active.classList.remove("active");
            quick_selection['is_active'] = false;
        };
    };

    manage_selection_status();
    get_list();
}

// Получаем список

async function get_list() {

    // Отборы
    var selection = {};

    selection['workspace'] = SelectionWorkspace.value;
    selection['department'] = SelectionDepartment.value;
    selection['status'] = SelectionStatus.value;
    selection['owner'] = SelectionOwner.value;
    selection['executor'] = SelectionExecutor.value;
    selection['project'] = SelectionProject.value;

    var response = await fetch(url,{
       method: "GET",
       headers: {
          "X-Requested-With": "XMLHttpRequest",
          "selection": JSON.stringify(selection),
          "quick-selection": JSON.stringify(quick_selection),
       }
    })

    TasksList.innerHTML = '';

    var data = await response.json();
    for (let item of data.context) {
        add_task_row(item);
    }

}

function get_inner_text(title) {

    var str_title = "";

    position = title.indexOf(" ", 25);
    if (position > 0) {
        str_title = title.slice(0, position+1) + "...";
    } else {
        str_title = title;
    }

    return str_title

}

function add_task_row(item) {

    var NewRow = document.createElement("tr");

    var RowTitle = document.createElement("td");
    RowTitleHref = document.createElement("a");
    RowTitleHref.href = item.url;
    RowTitleHref.innerHTML = get_inner_text(item.title);
    RowTitleHref.title = item.title;

    RowTitle.appendChild(RowTitleHref);

    if (item.new_messages > 0) {
        var RowTitleText = document.createElement("text");
        RowTitleText.style.color = "#712cf9";
        RowTitleText.innerHTML = " (<b>" + item.new_messages +"</b>)";

        RowTitle.appendChild(RowTitleText);
    }

    var RowStatus = document.createElement("td");
    RowStatus.innerHTML = item.status;

    var RowOwner = document.createElement("td");
    RowOwner.innerHTML = item.owner;

    var RowExecutor = document.createElement("td");
    RowExecutor.classList.add('table_row');
    RowExecutor.innerHTML = item.executor;

    var RowCreated_at = document.createElement("td");
    RowCreated_at.classList.add('table_row');
    var str_data = item.created_at.slice(0,10);
    RowCreated_at.innerHTML = `${str_data.slice(8,10)}.${str_data.slice(5,7)}.${str_data.slice(2,4)}`;

    var RowProject = document.createElement("td");
    RowProject.classList.add('table_row'); 
    RowProject.innerHTML = get_inner_text(item.project);
    RowProject.title = item.project;

    var RowWorkspace = document.createElement("td");
    RowWorkspace.classList.add('table_row');
    RowWorkspace.innerHTML = item.workspace;

    var RowDepartment = document.createElement("td");
    RowDepartment.classList.add('table_row');
    RowDepartment.innerHTML = item.department;

    NewRow.appendChild(RowTitle);
    NewRow.appendChild(RowStatus);
    NewRow.appendChild(RowOwner);
    NewRow.appendChild(RowExecutor);
    NewRow.appendChild(RowCreated_at);
    NewRow.appendChild(RowProject);
    NewRow.appendChild(RowWorkspace);
    NewRow.appendChild(RowDepartment);

    TasksList.append(NewRow);    

}

