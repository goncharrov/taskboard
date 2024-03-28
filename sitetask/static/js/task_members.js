
const AddMembersButton = document.querySelector('#members_add');
if (AddMembersButton != null) {
    AddMembersButton.addEventListener('click', () => add_member('add_member'))
}

const ParticipantList = document.querySelector("#participant-list");
const ParticipantForm = document.querySelector("#participant-form");
const ParticipantInput = document.querySelector("#id_user");

const UploadMembers = document.querySelector("#upload-members");
if (UploadMembers != null) {
    UploadMembers.addEventListener('click', () => add_member('upload_member'))
}

var url = window.location.href;

get_members();

// НЕ ЗНАЮ КАК ЭТО РАБОТАЕТ - РАЗОБРАТЬСЯ

function getCookie(name) {
  let cookieValue = null;
  if (document.cookie && document.cookie !== "") {
    const cookies = document.cookie.split(";");
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      // Does this cookie string begin with the name we want?
      if (cookie.substring(0, name.length + 1) === (name + "=")) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

async function get_members() {

    var response = await fetch(url,{
       method: "GET",
       headers: {
          "X-Requested-With": "XMLHttpRequest",
       }
    })

    ParticipantList.innerHTML = '';

    var data = await response.json()
    for (let item of data.context) {
        add_row(item);
    }

    // Очищаем поле ввода
    if (ParticipantInput != null) {
        ParticipantInput.value = "";
    }
}

function add_row(item) {

    ParticipantText = item.user;

    // Создаем тег tr с помощью создания элемента
    var NewParticipant = document.createElement("tr");

    var NameParticipant = document.createElement("td");
    NameParticipant.innerHTML = ParticipantText;

    NewParticipant.appendChild(NameParticipant);

    // Создаем кнопку Удалить
    var DelParticipant = document.createElement("td");
    DelParticipant.style["text-align"] = "right";

    if (ParticipantInput != null) {

        var DelButton = document.createElement("button");
        DelButton.setAttribute("role", "button");
        DelButton.title = "Удалить из списка участников";
        DelButton.className = "btn btn-light text-secondary border-0 taskboard_button_delete bi bi-trash";
        DelButton.id = "members_delete_" + item.id;
        DelButton.style["font-size"] = "0.8rem";
        DelButton.style["margin-right"] = "5px";
        DelParticipant.append(DelButton);

        // Добавляем событие по клику
        DelParticipant.addEventListener("click", function () {
            this.closest("tr").remove();
        });
    };

     NewParticipant.appendChild(DelParticipant);

    // Добавляем элемент на страницу
    ParticipantList.append(NewParticipant);
}

function add_member(type_operation) {

    var value = undefined;
    if (type_operation == 'add_member') {
        value = ParticipantInput.value;
    }

    if (value != '') {
        fetch(url, {
        method: "POST",
        credentials: "same-origin",
        headers: {
          "X-Requested-With": "XMLHttpRequest",
          "X-CSRFToken": getCookie("csrftoken"),
          "type-operation": type_operation,
        },
        body: JSON.stringify({user: value})
      })
      .then(response => response.json())
      .then(data => {
        if (data['status'] == "User is already member!") {
            alert("Пользователь уже состоит в участниках!");
        } else if (data['status'] == "User is already owner!") {
            alert("Пользователь и так является автором задачи!");
        } else if (data['status'] == "User is already executor!") {
            alert("Пользователь и так является исполнителем задачи!");
        } else if (data['status'] == "No project in task!") {
            alert("В сохраненной версии задачи не указан проект!");
        }
        get_members();
      });
    }
}

/////////////////////////////////////////////

ParticipantList.addEventListener('click', function (event) {
    if (event.target.localName == "button") {
        var del_id = event.target.id.slice(15);
        delete_member(del_id);
    }
});

function delete_member(del_id) {

    fetch(url, {
    method: "DELETE",
    credentials: "same-origin",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
    },
    body: JSON.stringify({member_id: del_id})
  })
  .then(response => response.json())
  .then(data => {
  });

}