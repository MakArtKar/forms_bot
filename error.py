import telebot
from telebot import types

import config
from db_worker import DataBase, User, Form
from import_to_google_sheets import post_in_sheets

bot = telebot.TeleBot(config.BOT_TOKEN)

@bot.message_handler(func=lambda message: True)
def main(message):
	with DataBase() as base:
		form = base.get_form('HDTfNbRFtPVO')
		print(form.creator_chat_id)
		bot.send_message(message.chat.id, 'OK')

if __name__ == '__main__':
    bot.infinity_polling()
