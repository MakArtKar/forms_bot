import telebot
import config
import os
import time
from db_worker import SQLighter

base = SQLighter(config.db_path)
bot = telebot.TeleBot(config.token)

# @bot.message_handler(commands=['test'])
# def find_file_ids(message):
#     #for file in os.listdir('music/'):
#     #    if file.split('.')[-1] == 'ogg':
#     #        f = open('music/'+file, 'rb')
#     #        msg = bot.send_voice(message.chat.id, f, None)
#     #        bot.send_message(message.chat.id, msg.message_id, reply_to_message_id=msg.message_id)
#     #    time.sleep(3)
#     bot.forward_message(message.chat.id, message.chat.id, 41)
#     bot.forward_message(message.chat.id, message.chat.id, 43)

# @bot.message_handler(content_types=['text'])
# def find_file_ids(message):
#     bot.send_message(message.chat.id, message.text)


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

	user.state = 0
	user.current_form = None
	user.current_question = None
	user.forms_number += 1
	base.update_user(user)


@bot.message_handler(content=['text'])
def answer(message):
	chat_id = message.chat.id
	user = base.get_user(chat_id)
	if user.state == 1:
		form_id = user.current_form
		question_id = user.current_question
		base.insert_message_to_question(form_id, question_id, message_id)


if __name__ == '__main__':
    bot.infinity_polling()
 