import sqlite3
import os
from dotenv import load_dotenv

# каталог этого файла (.../nsu_upprpo_deadlinebot/db) и корень проекта
_DB_DIR = os.path.dirname(os.path.abspath(__file__))
_PROJECT_ROOT = os.path.dirname(_DB_DIR)

# кладём переменные из db/.patch в окружение (путь абсолютный, не зависит от CWD)
load_dotenv(os.path.join(_DB_DIR, ".patch"))

# берём DB_PATH из окружения, иначе db/deadlines.db;
# относительный путь считаем от корня проекта, а не от текущей рабочей папки
_db_path = os.getenv("DB_PATH") or "db/deadlines.db"
if not os.path.isabs(_db_path):
    _db_path = os.path.join(_PROJECT_ROOT, _db_path)

DB_PATH = _db_path


def get_connection():
    """
    Функция для предоставления доступа к DB
    """
    # создаем объект класса Connection для открытия DB
    conect = sqlite3.connect(DB_PATH)
    # не игнорируем связи
    conect.execute("PRAGMA foreign_keys = ON")

    return conect
