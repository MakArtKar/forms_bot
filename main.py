import telebot
from telebot import types
from random import choice
from string import ascii_letters
from googleapiclient.errors import HttpError

import config
from db_worker import DataBase, User, Form
from import_to_google_sheets import post_in_sheets
from yaml_util import load_yml_file

bot = telebot.TeleBot(config.BOT_TOKEN)
messages_base = load_yml_file("messages.yml")

def send_question(message):
    with DataBase() as base:
        user = base.get_user(message.chat.id)
        form_id = user.current_form
        question_id = user.current_question

        form = base.get_form(form_id)
        if form.questions_number == user.current_question:
            user.current_form = None
            user.current_question = None
            user.state = config.States.DEFAULT.value
            bot.send_message(user.chat_id, messages_base["completed_form"])
            base.update_user(user)
            menu(message)
        else:
            messages_id = base.get_messages_id_from_question(form_id, question_id)
            for message_id in messages_id:
                bot.forward_message(user.chat_id, form.creator_chat_id, message_id)
            base.update_user(user)


@bot.message_handler(func=lambda message: message.text and len(message.text.split(' ')) == 2 and message.text.split(' ')[0] == '/start')
def answer_form(message):
    chat_id = message.chat.id
    with DataBase() as base:
        user = base.get_user(chat_id)
        if user.state != config.States.DEFAULT.value:
            bot.send_message(chat_id, 'TODO закончите создание/ответы на другую форму')
            return

        form_id = str(message.text.split(' ')[1])
        user.current_form = form_id
        user.current_question = 0
        user.state = config.States.ANSWERING_QUESTION.value
        base.update_user(user)

    send_question(message)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.ANSWERING_QUESTION.value)
def answer_question(message):
    chat_id = message.chat.id
    with DataBase() as base:
        user = base.get_user(message.chat.id)
        form_id = user.current_form
        question_id = user.current_question
        try:
            text = str(message.text)
        except:
            bot.send_message(chat_id, f'TODO неправильный формат ответа - введите текст')
            return
        base.insert_answer(chat_id, form_id, question_id, text)
        user.current_question += 1
        base.update_user(user)

    send_question(message)


@bot.message_handler(commands=['start'])
def menu(message):
    chat_id = message.chat.id

    keyboard = types.InlineKeyboardMarkup()
    button_new_forms = types.InlineKeyboardButton(text='Создать новую форму', callback_data='new_form')
    button_my_form = types.InlineKeyboardButton(text='Мои формы', callback_data='my_forms')
    keyboard.add(button_new_forms, button_my_form)
    
    bot.send_message(chat_id=chat_id, text='Выберите вариант', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'my_forms' and get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def my_forms(call):
    chat_id = call.message.chat.id
    
    keyboard = types.InlineKeyboardMarkup()
    with DataBase() as base:
        forms_id = base.get_user_forms(chat_id)
        for form_id in forms_id:
            form = base.get_form(form_id)
            button = types.InlineKeyboardButton(text=form.name, callback_data=f'my_form:{form.form_id}')
            keyboard.add(button)
    button = types.InlineKeyboardButton(text='Назад', callback_data='back_from_forms_list')
    keyboard.add(button)

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text='Ваши формы:', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'back_from_forms_list' and get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def back_from_forms_list(call):
    menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data.split(':')[0] == 'my_form' and 
    get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def request_form(call):
    form_id = call.data.split(':')[1]
    chat_id = call.message.chat.id

    keyboard = types.InlineKeyboardMarkup()
    button_import = types.InlineKeyboardButton(text='Импортировать в гугл таблицу', callback_data='import_to_google_sheets')
    button_erase = types.InlineKeyboardButton(text='Удалить форму', callback_data='erase_form')
    button_back = types.InlineKeyboardButton(text='Назад', callback_data='back_to_forms_list')
    keyboard.add(button_import)
    keyboard.add(button_erase)
    keyboard.add(button_back)

    with DataBase() as base:
        user = base.get_user(chat_id)
        user.current_form = form_id
        base.update_user(user)

        form = base.get_form(form_id)
        completed_number = len(base.get_all_answers(form_id))
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=call.message.message_id,
            text=messages_base["my_forms"].format(name=form.name, description=form.description, completed_number=completed_number),
            reply_markup=keyboard
        )


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_forms_list')
def back_to_forms_list(call):
    chat_id = call.message.chat.id

    with DataBase() as base:
        user = base.get_user(chat_id)
        user.current_form = None
        base.update_user(user)

    my_forms(call)



@bot.callback_query_handler(func=lambda call: call.data == 'erase_form' and
    get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def erase_form(call):
    chat_id = call.message.chat.id

    keyboard = types.InlineKeyboardMarkup()
    button_yes = types.InlineKeyboardButton(text='Да', callback_data='yes')
    button_no = types.InlineKeyboardButton(text='Нет', callback_data='no')
    keyboard.add(button_yes, button_no)

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text='Вы уверены, что хотите удалить форму?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'yes' and
    get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def agree_to_erase_form(call):
    chat_id = call.message.chat.id

    with DataBase() as base:
        user = base.get_user(chat_id)
        form_id = user.current_form
        base.delete_form(form_id)
        user.current_form = None
        base.update_user(user)

    menu(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'no' and
    get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def disagree_to_erase_form(call):
    with DataBase() as base:
        user = base.get_user(call.message.chat.id)
        form_id = user.current_form
    call.data = f'my_form:{form_id}'
    request_form(call)


@bot.callback_query_handler(func=lambda call: call.data == 'import_to_google_sheets' and 
    get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def import_form(call):
    chat_id = call.message.chat.id

    with DataBase() as base:
        user = base.get_user(chat_id)
        user.state = config.States.IMPORT_TO_GOOGLE_SHEETS.value
        base.update_user(user)

        keyboard = types.InlineKeyboardMarkup()
        button = types.InlineKeyboardButton(text='Назад', callback_data='back_to_form')
        keyboard.add(button)

        bot.send_message(chat_id, 'Введите ссылку на вашу гугл таблицу\nУбедитесь, что вы предоставили доступ по ссылке', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == 'back_to_form' and get_user_state(call.message.chat.id) == config.States.IMPORT_TO_GOOGLE_SHEETS.value)
def back_to_form(call):
    chat_id = call.message.chat.id

    with DataBase() as base:
        user = base.get_user(chat_id)
        form_id = user.current_form
        user.state = config.States.DEFAULT.value
        base.update_user(user)

    call.data = f'my_form:{form_id}'
    request_form(call)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.IMPORT_TO_GOOGLE_SHEETS.value)
def import_to_google_sheets(message):
    chat_id = message.chat.id
    spreadsheet_id = get_spreadsheet_id_from_ref(message.text)
    if (spreadsheet_id is None):
        bot.send_message(chat_id, 'TODO некорректная ссылка')
        with DataBase() as base:
            user = base.get_user(chat_id)
            user.state = config.States.DEFAULT.value
            base.update_user(user)
        
        menu(message)
        return

    with DataBase() as base:
        user = base.get_user(chat_id)
        form_id = user.current_form

        answers = base.get_all_answers(form_id)
        try:
            post_in_sheets(answers, spreadsheet_id)
        except HttpError as error:
            if (error._get_reason() == 'Requested entity was not found.'):
                bot.send_message(chat_id, 'TODO некорректная ссылка')
            elif (error._get_reason() == 'The caller does not have permission'):
                bot.send_message(chat_id, 'Проверьте, предоставили ли Вы доступ')
            else:
                bot.send_message(chat_id, 'Неизвестная ошибка')
        else:
            bot.send_message(chat_id, 'TODO OK')
            user.state = config.States.DEFAULT.value
            base.update_user(user)
            menu(message)


@bot.callback_query_handler(func=lambda call: call.data == 'new_form' and get_user_state(call.message.chat.id) == config.States.DEFAULT.value)
def make_form(call):
    chat_id = call.message.chat.id

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_default_name = types.KeyboardButton(text='Без названия')
    keyboard.add(button_default_name)

    with DataBase() as base:
        user = base.get_user(chat_id)

        bot.send_message(chat_id, 'Введите название формы', reply_markup=keyboard)
        
        user.state = config.States.FORM_NAME.value
        base.update_user(user)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.FORM_NAME.value)
def form_name(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_default_description = types.KeyboardButton(text='Без описания')
    keyboard.add(button_default_description)

    with DataBase() as base:
        chat_id = message.chat.id
        user = base.get_user(chat_id)

        form_id = generate_random_string()
        while not base.is_form_id_free(form_id):
            form_id = generate_random_string()

        user.current_form = form_id
        user.state = config.States.FORM_DESCRIPTION.value
        base.update_user(user)

        form = base.get_form(form_id)
        form.creator_chat_id = chat_id
        form.name = message.text
        base.update_form(form)

        bot.send_message(chat_id, 'Введите описание формы', reply_markup=keyboard)


@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.FORM_DESCRIPTION.value)
def form_description(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_new_question = types.KeyboardButton(text='Следующий вопрос')
    button_end_form = types.KeyboardButton(text='Закончить форму')
    keyboard.add(button_new_question, button_end_form)

    with DataBase() as base:
        chat_id = message.chat.id
        user = base.get_user(chat_id)

        form = base.get_form(user.current_form)
        form.form_description = message.text
        base.update_form(form)

        bot.send_message(chat_id, 'Введите вопрос', reply_markup=keyboard)

        user.state = config.States.MAKING_QUESTION.value
        user.current_question = 0
        base.update_user(user)


@bot.message_handler(func=lambda message: message.text == 'Следующий вопрос' and get_user_state(message.chat.id) == config.States.MAKING_QUESTION.value)
def new_question(message):
    with DataBase() as base:
        chat_id = message.chat.id
        bot.send_message(chat_id, 'Введите следующий вопрос')
        user = base.get_user(chat_id)

        user.current_question += 1
        base.update_user(user)


@bot.message_handler(func=lambda message: message.text == 'Закончить форму' and get_user_state(message.chat.id) == config.States.MAKING_QUESTION.value)
def end_form(message):
    with DataBase() as base:
        chat_id = message.chat.id
        user = base.get_user(chat_id)

        bot.send_message(chat_id, f'Ссылка на ваш опрос {config.REF + user.current_form}')

        form = base.get_form(user.current_form)
        form.questions_number = user.current_question + 1
        base.update_form(form)

        user.state = config.States.DEFAULT.value
        user.current_form = None
        user.current_question = None
        base.update_user(user)
        menu(message)

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.MAKING_QUESTION.value, 
    content_types=['text', 'photo', 'audio', 'sticker', 'document', 'voice'])
def add_message_to_question(message):
    with DataBase() as base:
        user = base.get_user(message.chat.id)
        form_id = user.current_form
        question_id = user.current_question
        base.insert_message_to_question(form_id, question_id, message.message_id)


def get_user_state(chat_id):
    with DataBase() as base:
        return base.get_user(chat_id).state


def generate_random_string(len=config.FORM_ID_LEN):
    return ''.join(choice(ascii_letters) for i in range(len))


def get_spreadsheet_id_from_ref(ref):
	try:
		return ref[ref.find('/d/'):].split('/')[2]
	except:
		return None

if __name__ == '__main__':
    bot.infinity_polling()
