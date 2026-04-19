from db.database import get_connection


def add_subject(user_id: int, name: str) -> int:
    """
    Функция добавляет новую строку в таблицу subjects.
    Вщзвращает: id созданной строки
    """
    # открываем db
    conect = get_connection()

    # вставляем значения в таблицу db и возвращаем объект с метадаными
    cursor = conect.execute(
        "INSERT INTO subjects (user_id, name) VALUES (?, ?)", (user_id, name)
    )

    # сохраняем изменения
    conect.commit()
    # узнаём id созданной строки
    subject_id = cursor.lastrowid()
    # закрываем db
    conect.close()

    return subject_id


def get_subjects(user_id: int) -> list[dict]:
    """

    """
    # открываем db
    conect = get_connection()

    # одбираем все строки с id, name для конкретного пользователя
    rows = conect.execute(
        "SELECT id, name FROM subjects WHERE user_id = ?", (user_id)
    ).fetchall() # забирает все строки из результата

    conect.commit()
    conect.close()

    return [{"id": row[0], "name": row[1]} for row in rows]


def delete_subject(user_id: int, subject_id: int) -> bool:
    """
    Функция удаляет конкретный предмет пользователя co вссеми tasks
    Возвращает: Bool удалено ли что-то или нет
    """
    conect = get_connection()

    # удаляем конкретный предмет пользователя и смотрим сколько строк удалено, метаданные 
    cursor = conect.execute(
        "DELETE FROM subjects WHERE id = ? AND user_id = ?",
        (subject_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0


