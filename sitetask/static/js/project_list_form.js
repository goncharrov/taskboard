var url = window.location.href;

document.querySelector('#id_apply_selection').addEventListener('click', get_list);
document.querySelector('#id_apply_active').addEventListener('click', get_active);
document.querySelector('#id_apply_completed').addEventListener('click', get_completed);

var ProjectsList = document.querySelector("#projects_list");

// Поля отбора
const SelectionWorkspace = document.querySelector("#id_workspace");
const SelectionDepartment = document.querySelector("#id_department");
const SelectionStatus = document.querySelector("#id_status");
const SelectionOwner = document.querySelector("#id_owner");

// Быстрые отборы

var quick_selection = {
    check_1_my_projects: "off",
    check_2_projects_participation: "off",
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
    quick_selection['check_1_my_projects'] = value;
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
    quick_selection['check_2_projects_participation'] = value;
    get_list();
}

function manage_selection_status() {

    if (quick_selection['is_active'] == true || quick_selection['is_completed'] == true) {
        SelectionStatus.disabled = true;
        SelectionStatus.value = "";
    }   else {
        SelectionStatus.disabled = false;
    };
    change_color_selection(SelectionStatus);

}

function get_active() {

    var button_active = document.querySelector('#id_apply_active');
    var button_completed = document.querySelector('#id_apply_completed');


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

function get_completed() {

    var button_active = document.querySelector('#id_apply_active');
    var button_completed = document.querySelector('#id_apply_completed');

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

async function get_list() {

    // Отборы
    var selection = {};

    selection['workspace'] = SelectionWorkspace.value;
    selection['department'] = SelectionDepartment.value;
    selection['status'] = SelectionStatus.value;
    selection['owner'] = SelectionOwner.value;

    var response = await fetch(url,{
       method: "GET",
       headers: {
          "X-Requested-With": "XMLHttpRequest",
          "selection": JSON.stringify(selection),
          "quick-selection": JSON.stringify(quick_selection),
       }
    })

    ProjectsList.innerHTML = '';

    var counter = 0;
    var data = await response.json();
    for (let item of data.context) {
        counter = counter + 1;
        add_project_row(item, counter);
    }

}

function get_inner_text(title, сharacters) {

    var str_title = "";

    position = title.indexOf(" ", сharacters);
    if (position > 0) {
        str_title = title.slice(0, position+1) + "...";
    } else {
        str_title = title;
    }

    return str_title

}

function add_project_row(item, counter) {

    var NewRow = document.createElement("tr");
    NewRow.className = "table-primary";

    var RowTitle = document.createElement("td");
    RowTitleHref = document.createElement("a");
    RowTitleHref.href = item.url;
    RowTitleHref.innerHTML = get_inner_text(item.title, 40);
    RowTitleHref.title = item.title;

    RowTitle.appendChild(RowTitleHref);

    var RowStatus = document.createElement("td");
    RowStatus.innerHTML = item.status;

    var RowOwner = document.createElement("td");
    RowOwner.innerHTML = item.owner;

    var RowCreated_at = document.createElement("td");
    RowCreated_at.classList.add('table_row'); 
    var str_data = item.created_at.slice(0,10);
    RowCreated_at.innerHTML = `${str_data.slice(8,10)}.${str_data.slice(5,7)}.${str_data.slice(2,4)}`;

    var RowWorkspace = document.createElement("td");
    RowWorkspace.classList.add('table_row'); 
    RowWorkspace.innerHTML = item.workspace;

    var RowDepartment = document.createElement("td");
    RowDepartment.classList.add('table_row'); 
    RowDepartment.innerHTML = item.department;

    if (item.tasks.length > 0) {
        var i_html = `
              <i
                class="bi bi-chevron-down"
                style="background-color: #c5d7f2">
              </i>
        `;
    } else {
        var i_html = "";
    }

    var RowCollapse = document.createElement("td");
    RowCollapse.innerHTML = `
        <button
          class="btn btn-light text-secondary border-0 taskboard_card-footer_buttons_table"
          style="background-color: #c5d7f2"
          data-bs-toggle="collapse"
          href="#collapse${counter}"
          role="button"
          aria-expanded="false"
          aria-controls="collapse${counter}">
          ${i_html}
        </button>
    `;

    NewRow.appendChild(RowTitle);
    NewRow.appendChild(RowStatus);
    NewRow.appendChild(RowOwner);
    NewRow.appendChild(RowCreated_at);
    NewRow.appendChild(RowWorkspace);
    NewRow.appendChild(RowDepartment);
    NewRow.appendChild(RowCollapse);

    ProjectsList.append(NewRow);

    if (item.tasks.length > 0) {
        add_tasks(counter, item.tasks);
    }

}

function add_tasks(counter, tasks) {

    var NewRowTr = document.createElement("tr");
    NewRowTr.className = "collapse";
    NewRowTr.id = `collapse${counter}`;

    var NewRowTd = document.createElement("td");
    NewRowTd.setAttribute("colspan", "7");

    var NewRowDiv = document.createElement("div");
    NewRowDiv.className = "d-flex justify-content-between pt-1";
    NewRowDiv.innerHTML = `
        <h6>Задачи по проекту:</h6>
        <a class="btn btn-link btn-sm" href="/tasks/add/" role="button" >Создать задачу</a>
    `;
    NewRowTd.append(NewRowDiv); 

    var NewRowTable = document.createElement("table");
    NewRowTable.className = "table mb-1 table-borderless";

    var NewRowTableHead = document.createElement("thead");
    NewRowTableHead.className = "table-light";
    NewRowTableHead.innerHTML = `
        <tr>
            <th scope="col">#</th>
            <th scope="col">Наименование</th>
            <th scope="col" Состояние</th>
            <th scope="col" class="table_row">Автор</th>
            <th scope="col" Исполнитель</th>
            <th scope="col" class="table_row">Создана</th>
        </tr>
    `;

    NewRowTable.append(NewRowTableHead); 

    var NewRowTableBody = document.createElement("tbody");

    for (let key in tasks) {
        // console.log(key, ':', tasks[key]);
        tasks_counter = Number(key) + 1;
        row_task = add_task_row(tasks[key], tasks_counter);
        NewRowTableBody.append(row_task);
    }

    NewRowTable.append(NewRowTableBody);

    NewRowTd.append(NewRowTable);
    NewRowTr.append(NewRowTd);
    ProjectsList.append(NewRowTr);

}

function add_task_row(item, counter) {   

    var NewRow = document.createElement("tr");

    var RowCounter = document.createElement("td");
    RowCounter.innerText = counter;

    var RowTitle = document.createElement("td");
    RowTitle.title = item.title;

    RowTitleHref = document.createElement("a");
    RowTitleHref.href = item.url;
    RowTitleHref.innerHTML = get_inner_text(item.title, 35);
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
    RowOwner.classList.add('table_row'); 
    RowOwner.innerHTML = item.owner;

    var RowExecutor = document.createElement("td");
    RowExecutor.innerHTML = item.executor;

    var RowCreated_at = document.createElement("td");
    RowCreated_at.classList.add('table_row'); 
    var str_data = item.created_at.slice(0,10);
    RowCreated_at.innerHTML = `${str_data.slice(8,10)}.${str_data.slice(5,7)}.${str_data.slice(2,4)}`;

    NewRow.appendChild(RowCounter);
    NewRow.appendChild(RowTitle);
    NewRow.appendChild(RowStatus);
    NewRow.appendChild(RowOwner);
    NewRow.appendChild(RowExecutor);
    NewRow.appendChild(RowCreated_at);

    return NewRow;

}