import os
from task.models import Task_Dispute


months = ['января', 'февраля', 'марта', 'апреля', 'мая', 'июня', 'июля', 'августа', 'сентября', 'октября', 'ноября',
'декабря']


def get_user_name(this_user) -> str:
    return f'{this_user.last_name} {this_user.first_name}'


def format_data(this_data) -> str:
    # return this_data.strftime("%d %b %Y в %H:%M")
    this_data_str = f'{this_data.day} {months[this_data.month - 1]} {this_data.year} в {this_data:%H:%M}'

    return this_data_str

# Получим обсуждение задачи
def get_task_dispute(pk) -> dict:

    image_extension = ['.jpg', '.JPG', '.jpeg', '.gif', '.bmp', '.png', '.heic']

    dispute = []
    dispute_qs = Task_Dispute.objects.filter(task__pk=pk).order_by('created_at')

    for message_qs in dispute_qs:

        is_image = False
        file_name = ''
        if message_qs.file:
            file_name = os.path.basename(message_qs.file.name)
            file_extension = os.path.splitext(file_name)[1]
            if file_extension in image_extension:
                is_image = True

        if message_qs.in_reply_task_dispute == 0:
            dispute.append(
                {'id': message_qs.id,
                'user': get_user_name(message_qs.user),
                'user_id': message_qs.user.id,
                'content': message_qs.content,
                'created_at': format_data(message_qs.created_at),
                'in_reply': [],
                'file': message_qs.file.url if message_qs.file else '',
                'IsImage': is_image,
                'FileName': file_name})
        else:
            found_message = list(filter(lambda message: message['id'] == message_qs.in_reply_task_dispute, dispute))
            if len(found_message) > 0:
                in_reply = found_message[0]['in_reply']
                in_reply.append(
                    {'id': message_qs.id,
                    'user': get_user_name(message_qs.user),
                    'user_id': message_qs.user.id,
                    'in_reply_user': get_user_name(message_qs.in_reply_user),
                    'content': message_qs.content,
                    'created_at': format_data(message_qs.created_at),
                    'file': message_qs.file.url if message_qs.file else '',
                    'IsImage': is_image,
                    'FileName': file_name})

    return {'dispute': dispute, 'message_quantity': dispute_qs.count()}


def get_current_message(message) -> dict:

    image_extension = ['.jpg', '.jpeg', '.gif', '.bmp', '.png', '.heic']

    is_image = False
    file_name = ''
    if message.file:
        file_name = os.path.basename(message.file.name)
        file_extension = os.path.splitext(file_name)[1]
        if file_extension in image_extension:
            is_image = True

    current_message = {
        'id': message.id,
        'user': get_user_name(message.user),
        'user_id': message.user.id,
        'content': message.content,
        'created_at': format_data(message.created_at),
        'in_reply': [],
        'file': message.file.url if message.file else '',
        'IsImage': is_image,
        'FileName': file_name}

    if message.in_reply_task_dispute == 0:
        current_message['main_message'] = True
    else:
        current_message['main_message'] = False
        current_message['in_reply_user'] = get_user_name(message.in_reply_user)

    return current_message
