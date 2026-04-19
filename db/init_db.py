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

    # сохраняем таблицы в базе данных 
    conect.commit()
    # закрываем базу данных
    conect.close()
