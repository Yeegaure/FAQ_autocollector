import telebot
import os
from dotenv import load_dotenv
from database import add_row, create_table
from faiss_db import add_vector
from utilities import (classify_message, normalize_question, normalize_answer,
                       similarity_check, retrieve_similar_answer, faiss_encode)
from pathlib import Path

env_path = Path(__file__).resolve().parent.parent / '.env'
load_dotenv(env_path)
TG_API_KEY = os.getenv('BOT_API_KEY')

bot = telebot.TeleBot(TG_API_KEY)

def classifier(message):
	txt = message.text
	result = classify_message(txt)
	bot.send_message(message.chat.id, '1' if result else '0')

@bot.message_handler(commands=['start'])
def start_message(message):
	bot.send_message(message.chat.id,'Привет! Я запоминаю все информативные вопросы из чата\n' \
						'и подскажу, если на похожий вопрос уже кто-то отвечал\n' 
						'чтобы я запомнил ответ, нужно на него ответить реплаем на соответствующий вопрос')

@bot.message_handler(commands=['classify'])
def classify(message):
	bot.send_message(message.chat.id,'Отправь мне сообщение и я его классифицирую')
	bot.register_next_step_handler_by_chat_id(message.chat.id, classifier)
 
# queue
PENDING_QUESTIONS = {} 

@bot.message_handler(content_types=['text'])
def handle_chat(message):
	text = message.text or ''

	if not message.from_user: return

	if message.from_user.is_bot: return

	if message.reply_to_message:
		parent_id = message.reply_to_message.message_id
		parent_key = (message.chat.id, parent_id)

		if parent_key in PENDING_QUESTIONS:
			question_text, answer_text = PENDING_QUESTIONS[parent_key], text

			question_norm = normalize_question(question_text)
			answer_norm = normalize_answer(answer_text)

			is_same, sql_id, dist = similarity_check(question_text)

			if is_same:
				bot.reply_to(message, 'Кажется, этот вопрос уже есть в базе знаний')
			else:
				new_id = add_row(question_norm, answer_norm)

				if new_id is None: return

				vector = faiss_encode(question_text)
				add_vector(vector, new_id)

				bot.reply_to(message, 'Я сохраню этот вопрос и ответ на него')

			del PENDING_QUESTIONS[parent_key]
			return
		return

	if '?' not in text and '？' not in text: return

	pred = classify_message(text)

	if not pred:
		bot.reply_to(message, '0')
		return
	retrieved_answer = retrieve_similar_answer(text)

	if retrieved_answer:
		bot.reply_to(message,f'Похожий вопрос уже задавали в этом чате. Такой ответ на него был дан:\n\n{retrieved_answer}')
		return

	PENDING_QUESTIONS[(message.chat.id, message.message_id)] = text

	bot.reply_to(message, 'На этот вопрос еще не отвечали, я его запомню')


if __name__ == '__main__':
	create_table()
	print('bot running ....')
	bot.infinity_polling()
