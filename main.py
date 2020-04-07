import telebot
import config


bot = telebot.TeleBot(config.token)

@bot.message_handler(content_types=['test'])
def find_file_ids(message):
    for file in os.listdir('music/'):
    	if file.split('.')[-1] == 'ogg':
    		f = open('music/'+file, 'rb')
    		msg = bot.send_voice(message.chat.id, f, NONE)
    		bot.send_message(message.chat.id, msg.voice.file_id, reply_to_message_id=msg.message_id)
    	time.sleep(3)

@bot.message_handler(content_types=['text'])
def find_file_ids(message):
    bot.send_message(message.chat.id, message.text)


if __name__ == '__main__':
    bot.infinity_polling()
