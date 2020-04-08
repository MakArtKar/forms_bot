import telebot
import config
import os
import time
from SQLighter import *

how_to_create_form = 'TODO написать инструкцию у созданию формы'

base = SQLighter()
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
def makeForm(message):
	chat_id = message.chat.id
	user = base.getUser(chat_id)
	if user.state != 0:
		bot.send_message(chat_id, 'TODO Пожалуйста, закончите предыдущую форму')
		pass

	form_id = chat_id + '_' + str(user.forms_number)
	form = base.getForm(form_id)
	bot.send_message(chat_id, how_to_create_form)
	
	user.updateState(1)
	user.updateCurrentForm(form_id)


@bot.message_handler(commands=['new_question'])
def makeQuestion(message):
	chat_id = message.chat.id
	user = base.getUser(chat_id)
	if user.state != 1:
		bot.send_message(chat_id, 'TODO создайте сначала форму/закончите опрос')
		pass

	form_id = user.current_form
	form = base.getForm(form_id)

	question_id = form.questions_number
	question = getQuestion(form_id, question_id)

	form.updateQuestionsNumber()
	user.updateCurrentQuestion(question_id)


@bot.message_handler(commands=['end_form'])
def endForm(message):
	chat_id = message.chat.id
	user = base.getUser(chat_id)
	if user.state != 1:
		bot.send_message(chat_id, 'TODO создайте сначала форму/закончите опрос')
		pass

	form_id = user.current_form
	form = base.getForm(form_id)

	user.updateState(0)
	user.updateCurrentForm(None)
	user.updateCurrentQuestion(None)
	user.updateFormsNumber()


def addMessageToQuestion(user, message_id):
	form_id = user.current_form
	question_id = user.current_question
	question = base.getQuestion(form_id, question_id)
	question.updateMessageIds(message_id)


@bot.message_handler(content=['text'])
def answer(message):
	chat_id = message.chat.id
	user = base.getUser(chat_id)
	if user.state == 1:
		if user.question_id != None:
			addMessageToQuestion(user, message.id)
		else:
			bot.send_message(chat_id, 'TODO сначала начните вопрос - /newquestion')


if __name__ == '__main__':
    bot.infinity_polling()
 