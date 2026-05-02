from db.database import get_connection



def add_subject(user_id: int, name: str, note: str = "") -> int:
    """
    Добавляет новый предмет пользователя в таблицу subjects.

    Параметры:
        user_id — id пользователя Telegram
        name — название предмета
        note — заметка к предмету: ссылки, пояснения, где лежат задания и т.д.
    Возвращает:
        id созданного предмета
    """
    # открываем db
    conect = get_connection()

    # вставляем значения в таблицу db и возвращаем объект с метадаными
    cursor = conect.execute(
        "INSERT INTO subjects (user_id, name, note) VALUES (?, ?, ?)", (user_id, name, note)
    )

    # сохраняем изменения
    conect.commit()
    # узнаём id созданной строки
    subject_id = cursor.lastrowid
    # закрываем db
    conect.close()

    return subject_id


def get_subjects(user_id: int) -> list[dict]:
    """
    Находит все предметы пользователя.

    Параметры:
        user_id — id пользователя Telegram
    Возвращает:
        список словарей с полями:
        id, name, note
    """
    # открываем db
    conect = get_connection()

    # одбираем все строки с id, name для конкретного пользователя
    rows = conect.execute(
        "SELECT id, name, note FROM subjects WHERE user_id = ?", (user_id,)
    ).fetchall() # забирает все строки из результата

    conect.commit()
    conect.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "note": row[2],
        }
        for row in rows
    ]


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
