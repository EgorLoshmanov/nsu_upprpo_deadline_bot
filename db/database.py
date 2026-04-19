import sqlite3
import os
from dotenv import load_dotenv

# кладем переменные из .patch в окружение 
load_dotenv(".patch")

# берем переменную DB_PATCH из окружения если нет то deadlines.db
DB_PATH = os.getenv("DB_PATH") or "deadlines.db"

def get_connection():
    """
    Фуннкцция для предостовления доступа к DB
    """
    # создаем объект класса Connection для открытия DB
    conect = sqlite3.connect(DB_PATH)
    # не игнорируем связи
    conect.execute("PRAGMA foreign_keys = ON")
    
    return conect