import telebot
import os
from dotenv import load_dotenv
from utilities import classify_message
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)
TG_API_KEY = os.getenv('BOT_API_KEY')

bot = telebot.TeleBot(TG_API_KEY)

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,'hello I am an informative questions ' \
	'classification bot.\nchoose the command "/classify"')

@bot.message_handler(commands=['classify'])
def classify(message):
	bot.send_message(message.chat.id,'Send me a question and I will classify it.')
	bot.register_next_step_handler_by_chat_id(message.chat.id, classifier)

def classifier(message):
	txt = message.text
	result = classify_message(txt)
	bot.send_message(message.chat.id, '1' if result else '0')

if __name__ == '__main__':
	print('bot running ....')
	bot.infinity_polling()

