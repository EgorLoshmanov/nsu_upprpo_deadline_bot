import sqlite3

from db.database import get_connection

def init_db():
    """
    Функция для разовой инициализации таблиц в базе данных
    """

    # открыли bd и получили объект класса Сonnection
    conect = get_connection()

    # создаем таблицу subjects если еще нет с id, user_id, name
    conect.execute("""
    CREATE TABLE IF NOT EXISTS subjects (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        name TEXT NOT NULL
    )
    """)

    # создаем таблицу tasks с id, user_id, subject_id, title, deadline, is_done
    conect.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        subject_id INTEGER REFERENCES subjects(id) ON DELETE CASCADE,
        title TEXT NOT NULL,
        deadline DATE NOT NULL,
        is_done INTEGER DEFAULT 0
    )
    """)

    # добавляем новые поля (OperationalError = столбец уже существует)
    try:
        conect.execute("ALTER TABLE subjects ADD COLUMN note TEXT")
    except sqlite3.OperationalError:
        pass

    try:
        conect.execute("ALTER TABLE tasks ADD COLUMN note TEXT")
    except sqlite3.OperationalError:
        pass

    # дата отметки выполнения — от неё считается автоудаление выполненных задач
    try:
        conect.execute("ALTER TABLE tasks ADD COLUMN done_at DATE")
    except sqlite3.OperationalError:
        pass
    # сохраняем таблицы в базе данных 
    conect.commit()
    # закрываем базу данных
    conect.close()
