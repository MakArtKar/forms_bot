import telebot
from telebot import types
from random import choice
from string import ascii_letters

import config
from db_worker import DataBase, User, Form
from import_to_google_sheets import post_in_sheets

bot = telebot.TeleBot(config.BOT_TOKEN)


def send_question(user):
    form_id = user.current_form
    question_id = user.current_question

    with DataBase() as base:
        form = base.get_form(form_id)
        messages_id = base.get_messages_id_from_question(form_id, question_id)
        if not messages_id:
            user.current_form = None
            user.current_question = None
            user.state = config.States.DEFAULT.value
            bot.send_message(user.chat_id, 'TODO спасибо, опрос закончен')
            base.update_user(user)
        else:
            for message_id in messages_id:
                bot.forward_message(user.chat_id, form.creator_chat_id, message_id)


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
    send_question(user)
    with DataBase() as base:
        base.update_user(user)


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
    send_question(user)
    with DataBase() as base:
        base.update_user(user)


@bot.message_handler(commands=['start'])
def menu(message):
    chat_id = message.chat.id

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_my_forms = types.KeyboardButton(text='Создать новую форму')
    button_new_form = types.KeyboardButton(text='Мои формы')
    button_answer_form = types.KeyboardButton(text='Пройти форму')
    keyboard.add(button_my_forms, button_new_form, button_answer_form)
    
    bot.send_message(chat_id, text='Выберите вариант', reply_markup=keyboard)


@bot.message_handler(func=lambda message: message.text == 'Создать новую форму')
def make_form(message):
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    button_default_name = types.KeyboardButton(text='Без названия')
    keyboard.add(button_default_name)

    with DataBase() as base:
        chat_id = message.chat.id
        user = base.get_user(chat_id)
        if user.state != config.States.DEFAULT.value:
            bot.send_message(chat_id, 'TODO Пожалуйста, закончите предыдущую форму')
            return

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
        if user.state != config.States.MAKING_QUESTION.value:
            bot.send_message(chat_id, 'TODO создайте сначала форму/закончите опрос')
            return

        user.current_question += 1
        base.update_user(user)


@bot.message_handler(func=lambda message: message.text == 'Закончить форму' and get_user_state(message.chat.id) == config.States.MAKING_QUESTION.value)
def end_form(message):
    with DataBase() as base:
        chat_id = message.chat.id
        user = base.get_user(chat_id)
        if user.state != config.States.MAKING_QUESTION.value:
            bot.send_message(chat_id, 'TODO создайте сначала форму/закончите проходить опрос')
            return

        bot.send_message(chat_id, f'Ссылка на ваш опрос {config.REF + user.current_form}')

        form = base.get_form(user.current_form)
        form.question_number = user.current_question
        base.update_form(form)

        user.state = config.States.DEFAULT.value
        user.current_form = None
        user.current_question = None
        base.update_user(user)

@bot.message_handler(func=lambda message: get_user_state(message.chat.id) == config.States.MAKING_QUESTION.value, 
    content_types=['text', 'photo', 'audio', 'sticker', 'document'])
def add_message_to_question(message):
    with DataBase() as base:
        user = base.get_user(message.chat.id)
        form_id = user.current_form
        question_id = user.current_question
        base.insert_message_to_question(form_id, question_id, message.message_id)


@bot.message_handler(commands=['import'])
def import_to_google_sheets(message):
  chat_id = message.chat.id
  try:
      form_id = str(message.text.split(' ')[1])
      spreadsheet_id = str(message.text.split(' ')[2])
  except:
      bot.send_message(chat_id, 'TODO Wrong format')
      return
  answers = base.get_all_answers(form_id)
  post_in_sheets(answers, spreadsheet_id)
  bot.send_message(chat_id, 'TODO OK')


def get_user_state(chat_id):
    with DataBase() as base:
        return base.get_user(chat_id).state


def generate_random_string(len=config.FORM_ID_LEN):
    return ''.join(choice(ascii_letters) for i in range(len))


if __name__ == '__main__':
    bot.infinity_polling()
 