import telebot
import os
from dotenv import load_dotenv

load_dotenv('.env')
TG_API_KEY = os.getenv('BOT_API_KEY')

bot = telebot.TeleBot(TG_API_KEY)
@bot.message_handler(commands=['start'])
def start_message(message):
  bot.send_message(message.chat.id,"Привет ✌️ ")
bot.infinity_polling()
