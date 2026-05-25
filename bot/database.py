import sqlite3
from pathlib import Path

db_path = Path(__file__).resolve().parent.parent / 'data' / 'faq.db'

def create_table():
    try:
        db_path.parent.mkdir(parents=True, exist_ok=True)

        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faq (
                       question_id INTEGER PRIMARY KEY AUTOINCREMENT,
                       question TEXT,
                       answer TEXT);
                ''')
            
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS faiss_mapping (
                       faiss_id INTEGER PRIMARY KEY,
                       sqlite_id INTEGER NOT NULL,
                       FOREIGN KEY (sqlite_id) REFERENCES faq(question_id));
                ''')
            conn.commit()

    except sqlite3.OperationalError as err:
        print(err)

def add_row(question: str, answer: str):
    try:
        create_table()
        with sqlite3.connect(db_path) as conn:        
            cursor = conn.cursor()
            cursor.execute('INSERT INTO faq (question, answer) VALUES(?, ?);', (question, answer))
            conn.commit()
            return cursor.lastrowid

    except sqlite3.OperationalError as err:
        print(err)
        return None
 
def get_row(question_id : int):
    try:
        create_table()
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT answer FROM faq WHERE question_id=?', (question_id,))
            answer = cursor.fetchone()
            return answer[0] if answer else None
    
    except sqlite3.OperationalError as err:
        print(err)
        return None
