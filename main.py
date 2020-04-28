import telebot
import config
import os
import time
from db_worker import SQLighter
from import_to_google_sheets import post_in_sheets

base = SQLighter(config.db_path)
bot = telebot.TeleBot(config.token)


@bot.message_handler(commands=['test'])
def test(message):
	answers = base.get_all_answers('375622021_0')
	post_in_sheets(answers, '1g5RCS_JUx3T9SprG87toHl1jesLEKa0YEsG_OxfFRN8')

# @bot.message_handler(commands=['import'])
# def import_to_google_sheets(message):
# 	bot.send_message()

@bot.message_handler(commands=['new_form'])
def make_form(message):
	chat_id = message.chat.id
	user = base.get_user(chat_id)
	if user.state != 0:
		bot.send_message(chat_id, 'TODO Пожалуйста, закончите предыдущую форму')
		return

	bot.send_message(chat_id, 'TODO инструкция по созданию формы')
	
	form_id = str(chat_id) + '_' + str(user.forms_number)
	user.state = 1
	user.current_form = form_id
	user.current_question = 0
	base.update_user(user)


@bot.message_handler(commands=['new_question'])
def make_question(message):
	chat_id = message.chat.id
	bot.send_message(chat_id, 'TODO введите ваш вопрос')
	user = base.get_user(chat_id)
	if user.state != 1:
		bot.send_message(chat_id, 'TODO создайте сначала форму/закончите опрос')
		return

	user.current_question += 1
	base.update_user(user)


@bot.message_handler(commands=['end_form'])
def endForm(message):
	chat_id = message.chat.id
	user = base.get_user(chat_id)
	if user.state != 1:
		bot.send_message(chat_id, 'TODO создайте сначала форму/закончите проходить опрос')
		return

	bot.send_message(chat_id, f'TODO ваш индефикатор опроса {user.current_form}')

	user.state = 0
	user.current_form = None
	user.current_question = None
	user.forms_number += 1
	base.update_user(user)


@bot.message_handler(commands=['answer_form'])
def answer_form(message):
	chat_id = message.chat.id
	user = base.get_user(chat_id)	
	if user.state != 0:
		bot.send_message(chat_id, 'TODO закончите создание/ответы на другую форму')
		return

	bot.send_message(chat_id, 'TODO введите индефикатор опроса')
	user.state = 2
	base.update_user(user)

def send_question(user):
	form_id = user.current_form
	question_id = user.current_question
	creator_chat_id = int(form_id.split('_')[0])
	messages_id = base.get_messages_id_from_question(form_id, question_id)
	if not messages_id:
		user.current_form = None
		user.current_question = None
		user.state = 0
		bot.send_message(user.chat_id, 'TODO спасибо, опрос закончен')
		return
	for message_id in messages_id:
		bot.forward_message(user.chat_id, creator_chat_id, message_id)

@bot.message_handler(content_types=['text'])
def answer(message):
	chat_id = message.chat.id
	user = base.get_user(chat_id)
	if user.state == 1:
		form_id = user.current_form
		question_id = user.current_question
		base.insert_message_to_question(form_id, question_id, message.message_id)
	elif user.state == 2:
		if user.current_form == None:
			try:
				form_id = str(message.text)
				args = form_id.split('_')
				assert len(args) == 2
				creator_chat_id, form_number_id = int(args[0]), int(args[1])
				creator_user = base.get_user(creator_chat_id, insert_if_not_exists=False)
				assert creator_user != None and 0 <= form_number_id and form_number_id < creator_user.forms_number
			except:
				bot.send_message(chat_id, 'TODO неверный индефикатор')
				return
			user.current_form = form_id
			user.current_question = 0
			send_question(user)
			base.update_user(user)
		else:
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
			base.update_user(user)


if __name__ == '__main__':
    bot.infinity_polling()
 