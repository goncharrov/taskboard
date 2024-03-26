var url = window.location.href;

var uploadFile = undefined;

// Верхнее поле ввода сообщения
var text_input_top = document.querySelector("#text-input-top");
document.querySelector('#add-message-top').addEventListener('click', () =>  add_message(text_input_top.value,"top"));


// Нижнее поле ввода сообщения
var is_add_message_bottom = document.querySelector('#add-message-bottom');
if (is_add_message_bottom != null) {
    var text_input_bottom = document.querySelector("#text-input-bottom");
    is_add_message_bottom.addEventListener('click', () =>  add_message(text_input_bottom.value,"bottom"));
}

// Выводим сообщения
const DisputeList = document.querySelector("#dispute-list");

//get_dispute();

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

async function get_dispute() {

    var response = await fetch(url,{
       method: "GET",
       headers: {
          "X-Requested-With": "XMLHttpRequest",
       }
    })

    DisputeList.innerHTML = '';

    var data = await response.json();
    for (let message of data.context) {
        add_message_html(message);
    }

}

/////////////////////////////////////////////////////////////

// ВЫВОДИМ ДАННЫЕ В МАКЕТ - НАЧАЛО

function get_input_group_button(message_id) {

    var html = `

    <div class="input-group d-flex align-items-start">
      <div class="btn-group-vertical" role="group" aria-label="Vertical button group">
        <div class="input-group-text bg-transparent border-0 taskboard_card-footer_buttons">
          <input type="file" id="upload-file-${ message_id }" hidden="hidden">
          <button class="btn btn-light text-secondary">
            <label for="upload-file-${ message_id }">
              <i class="bi bi-paperclip" style="font-size: 1rem" title="Добавить изображение"></i>
            </label>
          </button>
        </div>
      </div>

      <textarea
        class="form-control border-0"
        id="text-input-${ message_id }"
        placeholder="Ваше сообщение..."
        rows="3"
      ></textarea>

      <div class="input-group-text bg-transparent border-0 taskboard_card-footer_buttons">
        <button class="btn btn-light text-secondary" id="button-add-message-${ message_id }">
          <i class="bi bi-send" id="add-message-${ message_id }" style="font-size: 1rem" title="Отправить сообщение"></i>
        </button>
      </div >
    </div>`;

    return html;

}

function get_div_ansver(message) {

    var html = `

    <div>
      <div class="small">
        <i class="bi bi-chat-left ms-1" style="font-size: 1rem"></i>
        <a
          class="taskboard_sidebar_heading"
          style="color: #77808c"
          data-bs-toggle="collapse"
          data-bs-target="#message_collapse-${ message.id }"
          aria-expanded="false"
          aria-controls="message_collapse-${ message.id }"
          href=""
          >ОТВЕТИТЬ
        </a>
      </div>
    </div>`;

    return html;

}

function get_div_file(message) {

    if (message.file == '') {
        return `<div><pre>${ message.content }</pre></div>`;
    }

    var div_image = `
      <div>
        <img
           src="${ message.file }"
           class="img-thumbnail" style="max-width: 320px; max-height: 250px"
           alt="{{ message.content }}"
        >
        <div style="max-width: 320px"><pre>${ message.content }</pre></div>
      </div>`;

    var div_any_file = `
      <div>
        <i class="bi bi-file-earmark" style="font-size: 1rem;"></i>
        <a href="${ message.file } " title="${ message.FileName }">${ message.FileName }</a>
        <div style="max-width: 320px"><pre>${ message.content }</pre></div>
      </div>`;

      if (message.IsImage == true) {
        return div_image;
      } else {
        return div_any_file;
      }
}

function add_message_html(message, user_id) {

    var input_group_button = get_input_group_button(message.id);
    var div_ansver = get_div_ansver(message);
    var div_file = get_div_file(message);

    var style_card_color = message.user_id == user_id ? 'style="background-color: rgba(var(--bd-violet-rgb), 0.2);"' : ''
    console.log(message.user_id,user_id);

    var message_html = `

    <div class="d-flex align-items-srart mt-3">
      <div class="pe-2">
        <div class="card taskboard_message d-inline-block p-2 px-3 m-1" ` + style_card_color + `>
          <div class="d-flex mb-1">
            <div style="font-weight: bold">${ message.user }&nbsp</div>
            <div class="d-none d-md-block" style="color: grey">${ message.created_at }</div>
          </div>`
            + div_file + `
          <div class="d-md-none mt-1" style="color: grey">${ message.created_at }</div>
        </div>`
            + div_ansver + `
        <div class="collapse" id="message_collapse-${ message.id }">
          <div class="card mb-1 mt-2">`
            + input_group_button + `
          </div>
        </div>
      </div>
    </div>`;

    for (let reply_message of message.in_reply) {
           message_html = message_html + add_reply_message_html(reply_message);
    };

    var DisputeDiv = document.createElement("div");
    DisputeDiv.innerHTML = message_html;
    DisputeList.append(DisputeDiv);

}

function add_reply_message_html(reply_message, user_id) {

    var input_group_button = get_input_group_button(reply_message.id);
    var div_ansver = get_div_ansver(reply_message);
    var div_file = get_div_file(reply_message);

    var style_card_color = reply_message.user_id == user_id ? 'style="background-color: rgba(var(--bd-violet-rgb), 0.2);"' : ''

    var message_html = `

    <div class="d-flex align-items-srart mt-2 mb-3 ms-5">
        <div class="pe-2">
          <div class="card taskboard_message d-inline-block p-2 px-3 m-1" ` + style_card_color + `>
            <div class="d-flex">
              <div style="font-weight: bold"> ${ reply_message.user } &nbsp</div>
              <i
                class="bi bi-arrow-right"
                style="font-size: 1rem"
              ></i>
              <div style="font-weight: bold">&nbsp ${ reply_message.in_reply_user } &nbsp</div>
              <div class="d-none d-md-block" style="color: grey">${ reply_message.created_at }</div>
            </div>`
            + div_file + `
            <div class="d-md-none mt-1" style="color: grey">${ reply_message.created_at }</div>
          </div>`
            + div_ansver + `
          <div class="collapse" id="message_collapse-${ reply_message.id }">
            <div class="card mt-2">`
                + input_group_button + `
            </div>
          </div>
        </div>
    </div>`;

    return message_html;

}

// ВЫВОДИМ ДАННЫЕ В МАКЕТ - ОКОНЧАНИЕ

// ЗАПИСЫВАЕМ ДАННЫЕ В БД ПО ОБЩЕМУ ВЕРХНЕМУ ИНПУТУ - НАЧАЛО

function clean_message_id(message_id) {
    if (message_id == 'top') {
        text_input_top.value = "";
        document.querySelector("#message_collapse").classList.remove('show');
    } else if (message_id == 'bottom') {
        text_input_bottom.value = "";
        document.querySelector("#message_collapse-end").classList.remove('show');
    } else {
        document.querySelector("#text-input-"+message_id).value = "";
        document.querySelector("#message_collapse-"+message_id).classList.remove('show');
    }
}

function add_message_row(message, user_id) {
    if (message.main_message == true) {
        add_message_html(message, user_id);
    } else {
        let message_html = add_reply_message_html(message, user_id);
        let DisputeDiv = document.createElement("div");
        DisputeDiv.innerHTML = message_html;
        DisputeList.append(DisputeDiv);
    }
}

function add_message(value, message_id) {

    value = value.trim();

    if ( !value ) {
        alert("Введите текст сообщения!");
        return;
    }

    var mess_id = (message_id == 'top' || message_id == 'bottom') ? 0 : message_id;

    fetch(url, {
    method: "POST",
    credentials: "same-origin",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
      "type-message": "send-text",
    },
    body: JSON.stringify({message: value, id: mess_id})
    })
    .then(response => response.json())
    .then(data => {
        //get_dispute();
        console.log(data);
        add_message_row(data.message, data.user_id);
        clean_message_id(message_id);
    });

}

///////////////////////////////////////////////////

// ЗАПИСЫВАЕМ ДАННЫЕ В БД В ОТВЕТ НА ДРУГОЕ СООБЩЕНИЕ - НАЧАЛО

DisputeList.addEventListener('click', function (event) {

//    console.log(event.target.localName)

    if (event.target.localName == "button") {
        if ((event.target.id.slice(0,18)) == "button-add-message") {
             input_id = event.target.id.slice(19);
             add_message(document.querySelector("#text-input-"+input_id).value, input_id);
        }
    } else if (event.target.localName == "i") {
        if ((event.target.id.slice(0,11)) == "add-message") {
             input_id = event.target.id.slice(12);
             add_message(document.querySelector("#text-input-"+input_id).value, input_id);
        }
    } else if (event.target.localName == "input") {
        if ((event.target.id.slice(0,11)) == "upload-file") {
            uploadFile = document.getElementById(event.target.id);
            uploadFile.value = "";
            uploadFile.addEventListener('change', () => {
                uploadFileWhenСhanges(uploadFile);
            })
        }
    }
})

// ЗАПИСЫВАЕМ ДАННЫЕ В БД В ОТВЕТ НА ДРУГОЕ СООБЩЕНИЕ - ОКОНЧАНИЕ

/////////////////////////////////////////////////////////////
/////////////////////////////////////////////////////////////
// ОТПРАВКА ФАЙЛА НА СЕРВЕР

// Реквизиты формы отправки файла
const fileForm = document.getElementById('send_file_form');
const openFileForm = document.getElementById('open_file_form');

const sendFileForm = document.getElementById('file_form_send');
const closeFileForm = document.getElementById('file_form_close');

const image_file_background = document.getElementById('picture-background');
const image_file = document.getElementById('image_file');

const file_background = document.getElementById('file-background');
const file_name = document.getElementById('file-name');

//////////////////////////////////////////////////////////////////
// Ставим прослушку на upload файлы

const uploadFileTop = document.getElementById('upload-file-top');
uploadFileTop.addEventListener('click', () => {
    uploadFile = uploadFileTop;
    uploadFile.value = '';
})

uploadFileTop.addEventListener('change', () => {
    uploadFileWhenСhanges(uploadFileTop);
})

const uploadFileBottom = document.getElementById('upload-file-bottom');
if (uploadFileBottom != null) {
    // Очистим при клике
    uploadFileBottom.addEventListener('click', () => {
        uploadFile = uploadFileBottom;
        uploadFile.value = '';
    })
    // Отследим изменение
    uploadFileBottom.addEventListener('change', () => {
        uploadFileWhenСhanges(uploadFileBottom);
    })
}

/////////////////////////////////////////////////////////////////

function uploadFileWhenСhanges(uploadFile) {

    upload_file = uploadFile.files[0];
//    console.log(upload_file);

    if (upload_file.type == 'application/x-msdownload') {
        uploadFile.value = '';
        alert('Отправка исполнимых файлов запрещена!');
        return;
    }

//    if ( !upload_file.type.match('image') && !upload_file.type.match('pdf') && !upload_file.type.match('x-zip-compressed') ) {
//        uploadFile.value = '';
//        alert('Невозможно загрузить файл выбранного формата. Для отправки файла запакуйте его в zip-архив!');
//        return;
//    }

    fileForm.classList.add('active');
    document.getElementById('send_file_body_input').focus();

    var fReader = new FileReader();
    fReader.readAsDataURL(uploadFile.files[0]);
    fReader.onloadend = function(event){
        image_file.src = event.target.result;
    };

    if (uploadFile.files[0].type.substr(0, 5) == 'image') {
        image_file_background.classList.add('active');
        openFileForm.style.height = '310px';
    } else {

        file_background.classList.add('active');
        openFileForm.style.height = '55px';

        var uploadFileName = uploadFile.files[0].name;
        if (uploadFileName.length > 30) {
            let uploadFileNameBeginning = uploadFileName.substr(0, 15);
            let uploadFileNameEnding = uploadFileName.substr(-15);
            file_name.innerText = uploadFileNameBeginning + '...' + uploadFileNameEnding;
        } else {
            file_name.innerText = uploadFile.files[0].name;
        }
    }

}

///////////////////////////////////////////////////////////////////////////
//////////////////////////////////////////////////////////////////////////

function closeForm() {
    fileForm.classList.remove('active');
    file_background.classList.remove('active');
    image_file_background.classList.remove('active');
    image_file.src = '';
    document.getElementById('send_file_body_input').value = '';
}

closeFileForm.addEventListener('click', () => {
    closeForm();
})

sendFileForm.addEventListener('click', () => {

    if (uploadFile.files[0].size > 2097152) {
        alert('Разрешается загружать файлы размером не более 2 мб!');
        closeForm();
    } else {
        if (uploadFile.files[0].type == 'image/bmp') {
            alert('При загрузке изображений используйте файлы форматов jpg, jif, png !');
            closeForm();
        } else {
            SendFileMessage();
        }
    }

})

function SendFileMessage() {

    caption = document.getElementById('send_file_body_input').value;
    caption = caption.trim();

    uploadFile_id = uploadFile.id.slice(12);
    var message_id = (uploadFile_id == 'top' || uploadFile_id == 'bottom') ? 0 : uploadFile_id;

    if ( !uploadFile.files[0]) {
        alert("Выберите файл!");
        return;
    }

    const formData = new FormData();
    formData.append('file', uploadFile.files[0]);
    formData.append('caption', caption);
    formData.append('id', message_id);
    formData.append('action', 'send-file')

    fetch(url, {
    method: "POST",
    headers: {
      "X-Requested-With": "XMLHttpRequest",
      "X-CSRFToken": getCookie("csrftoken"),
      "type-message": "send-file",
    },
    body: formData,
    })

    .then(response => response.json())
    .then(data => {
        //get_dispute();
        add_message_row(data.message, data.user_id);
        clean_message_id(uploadFile_id);

    });

    closeForm();

}

