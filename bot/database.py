import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent / 'data' / 'faq.db'

def create_table():
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faq (
                       question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT,
                       answer TEXT);
                ''')
            conn.commit()

    except sqlite3.OperationalError as err:
        print(err)

def add_row(question : str, answer : str):
    try:
        with sqlite3.connect(db_path) as conn:        
            cursor = conn.cursor()
            cursor.execute('INSERT INTO faq (question, answer) VALUES(?, ?);', (question, answer))
            return cursor.lastrowid

    except sqlite3.OperationalError as err:
        print(err)

# TODO : probably we need to make it search by question, not by index
def get_row(question_id : int):
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT answer FROM faq WHERE question_id=?', (question_id,))
        answer = cursor.fetchone()
        return answer[0] if answer else None
    
    except sqlite3.OperationalError as err:
        print(err)
    


    

