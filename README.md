# FAQ Autocollector from Group Chats in Messengers

FAQ Autocollector is a Telegram bot that automatically collects useful question-answer pairs from group chats and reuses them when similar questions appear again.

The project is designed for chats where users often ask repeated questions. Instead of manually maintaining a FAQ, the bot observes new messages, detects informative questions, waits for a direct reply from another user, saves the completed question-answer pair, and later suggests the saved answer for similar questions.

## Report

Project report: **[https://drive.google.com/file/d/1eOmXQq59lBdJ0HkzLMAtLgGOCaGj3K1B/view?usp=drive_link]**

## Main Features

* Detects candidate questions in Telegram group chats.
* Classifies whether a question is informative or not.
* Stores unanswered informative questions in a temporary queue.
* Saves an answer only when another user replies directly to the original question.
* Normalizes saved questions and answers using an LLM.
* Stores question-answer text pairs in SQLite.
* Stores question vectors in FAISS for similarity search.
* Retrieves a saved answer when a similar question appears again.

## How It Works

The bot processes messages in the following way:

1. A new text message appears in the Telegram chat.
2. The bot ignores messages from bots and messages that are not questions.
3. If the message is a question, it is classified by a Logistic Regression model.
4. If the question is not informative, the bot ignores it or returns `0` in debug mode.
5. If the question is informative, the bot searches for a similar question in FAISS.
6. If a similar question already exists, the bot retrieves the related answer from SQLite and sends it to the chat.
7. If no similar question is found, the bot adds the original question to the temporary queue.
8. When another user replies directly to this queued question, the bot treats the reply as an answer.
9. The question and answer are normalized.
10. The normalized question-answer pair is saved to SQLite.
11. The original question is vectorized and added to the FAISS index.
12. The mapping between the FAISS vector position and the SQLite `question_id` is saved in `map.npy`.

## Project Structure

```text
FAQ_autocollector/
│
├── bot/
│   ├── bot.py                    # Main Telegram bot logic
│   ├── utilities.py              # Text cleaning, classification, normalization, retrieval
│   ├── database.py               # SQLite database functions
│   ├── faiss_db.py               # FAISS vector index and mapping logic
│   ├── log_regression_model.pkl  # Trained Logistic Regression classifier
│   └── vectorizer.pkl            # Saved text vectorizer
│
├── data/                         # Runtime storage for SQLite, FAISS index, and map.npy
├── requirements.txt              # Python dependencies
└── README.md
```

## Storage

The project uses three main storage components:

```text
faq.db       -> stores normalized question-answer pairs
faiss.index  -> stores vector representations of questions
map.npy      -> connects FAISS vector positions with SQLite question_id values
```

SQLite stores readable text data, while FAISS is used only for vector similarity search. Since FAISS does not store answers, the `map.npy` file is needed to connect each FAISS vector position with the corresponding row in the SQLite database.

## Installation

### 1. Clone the repository

```bash
git clone https://github.com/Yeegaure/FAQ_autocollector.git
cd FAQ_autocollector
```

### 2. Create and activate a virtual environment
```bash
python -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` file

Create a `.env` file in the root folder of the project:

```text
BOT_API_KEY=your_telegram_bot_token

API_KEY=your_llm_api_key
MODEL=your_llm_model_name
URL=your_llm_base_url

SYSTEM_PROMPT_QUESTION=your_prompt_for_question_normalization
SYSTEM_PROMPT_ANSWER=your_prompt_for_answer_normalization
```

`BOT_API_KEY` is required to run the Telegram bot.

The LLM-related variables are used for question and answer normalization.

### 5. Run the bot

```bash
python bot/bot.py
```

After launch, the bot starts polling Telegram updates.

## Telegram Commands

### `/start`

Shows a short explanation of how the bot works.

### `/classify`

Allows testing whether a message is classified as informative or not.

## Example Scenario

1. A user asks a new informative question in the chat.
2. The bot checks that no similar question exists in the knowledge base.
3. The bot says that this question has not been answered before and remembers it temporarily.
4. Another user replies directly to that question.
5. The bot normalizes the question and answer.
6. The bot saves the pair to the database.
7. Later, when a similar question appears, the bot retrieves the saved answer and sends it to the chat.

## Architecture

The project has a modular monolithic architecture. It is divided into several Python modules, but all components run as one application and communicate through direct function calls.

Main modules:

* `bot.py` — handles Telegram messages and coordinates the full pipeline.
* `utilities.py` — performs text cleaning, classification, vectorization, normalization, similarity checking, and answer retrieval.
* `database.py` — manages the SQLite database.
* `faiss_db.py` — manages the FAISS vector index and the `map.npy` mapping file.
