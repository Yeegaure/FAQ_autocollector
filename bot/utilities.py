import emoji
import pickle
import warnings
import os
import numpy as np
from dotenv import load_dotenv
from database import get_row, add_row
import faiss_db

from langchain_openai import ChatOpenAI
from langchain_core.output_parsers import StrOutputParser
from langchain_core.messages import SystemMessage, HumanMessage

from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings('ignore', category=InconsistentVersionWarning)

BASE_DIR = os.path.dirname(__file__)
load_dotenv()
API_KEY = os.getenv('API_KEY')

with open(os.path.join(BASE_DIR, 'log_regression_model.pkl'), 'rb') as file:
    log_reg = pickle.load(file)

with open(os.path.join(BASE_DIR, 'vectorizer.pkl'), 'rb') as file:
    vectorizer = pickle.load(file)

def clean_message(message : str) -> str:
    message = emoji.replace_emoji(message, '')
    message = message.strip()
    return message

def classify_message(message : str) -> bool:
    message_cleaned = clean_message(message)
    X = vectorizer.transform([message_cleaned])
    pred = log_reg.predict(X)[0]

    return bool(pred)

def faiss_encode(message : str):
    message_cleaned = clean_message(message)
    X_vectorized = vectorizer.transform([message_cleaned])
    X_dense = X_vectorized.toarray().astype('float32')
    return X_dense

class LLM_normalizer:
    
    def __init__(self, model, API_KEY, SYSTEM_PROMPT, url):
        self.parser = StrOutputParser()
        self.model = model
        self.API_KEY = API_KEY
        self.SYSTEM_PROMPT = SYSTEM_PROMPT
        self.url = url
        self.cache = {}
        
    def normalize_text(self, text: str) -> str:
        '''try 3 times if fails => original text + check if question text is the same => use cache: no LLM call'''
        text = emoji.replace_emoji(str(text), '')
        if text in self.cache:
            return self.cache[text]
        llm = ChatOpenAI(api_key=self.API_KEY, base_url=self.url, model=self.model)

        for _ in range(3):
            message = [SystemMessage(content=self.SYSTEM_PROMPT), HumanMessage(content=str(text))]
            llm_response = llm.invoke(message)
            raw = self.parser.invoke(llm_response).strip()
            if raw:
                self.cache[text] = raw
                return raw

        self.cache[text] = text
        return text

def similarity_check(question, threshold: float=27):
    sql_ids, dist = faiss_db.search_and_encode(question, k=1)
    if not sql_ids or not dist:
        return False, None, None

    nearest_dist = float(dist[0])
    if nearest_dist <= threshold:
        return True, sql_ids[0], nearest_dist
    return False, None, nearest_dist

def retrieve_similar_answer(question, threshold=27):
    is_same, sql_id, dist = similarity_check(question, threshold)
    if not is_same:
        return None
    result = get_row(sql_id)
    return result

def normalize_question(text: str) -> str:
    SYSTEM_PROMPT_QUESTION = os.getenv('SYSTEM_PROMPT_QUESTION')
    model = os.getenv('MODEL')
    url = os.getenv('URL')

    normalizer = LLM_normalizer(model=model, API_KEY=API_KEY, SYSTEM_PROMPT=SYSTEM_PROMPT_QUESTION, url=url)
    return normalizer.normalize_text(text)

def normalize_answer(text:str) -> str:
    SYSTEM_PROMPT_ANSWER = os.getenv('SYSTEM_PROMPT_ANSWER')
    model = os.getenv('MODEL')
    url = os.getenv('URL')

    normalizer = LLM_normalizer(model=model, API_KEY=API_KEY, SYSTEM_PROMPT=SYSTEM_PROMPT_ANSWER, url=url)
    return normalizer.normalize_text(text)

if __name__ == '__main__':
    print('Testing utilities...')
    test = "интересно😮 так а толку то от педиатра, скажет аллергия или энтеровирус (былотакое), напишите пожалуйста как сьездите. а к дерматологу куда? на сухэ батора?"
    print('input : ', test)
    print('cleaned ', clean_message(test))
    print('prediction :', classify_message(test))