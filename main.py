import telebot
import config
import os
import time
from SQLighter import *


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
		bot.send_message(chat_id, 'Пожалуйста, закончите предыдущую форму')
		pass

	form = base.addForm(chat_id + '_' + user.forms_number)
	user = base.updateUser
	base.updateState()

@bot.message_handler(commands=['new_question'])
def makeQuestion(message):


if __name__ == '__main__':
    bot.infinity_polling()
 

