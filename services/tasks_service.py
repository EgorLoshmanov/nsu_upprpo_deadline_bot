from db.database import get_connection

from utils import parse_deadline



def add_task(user_id, subject_id, title, deadline_str) -> int:
    """
    Функция добавляет новое задание
    возвращает id нового task
    """
    conect = get_connection()

    deadline_str = str(parse_deadline(deadline_str))

    cursor = conect.execute(
        "INSERT INTO tasks (user_id, subject_id, title, deadline) VALUES (?, ?, ?, ?)", 
        (user_id, subject_id, title, deadline_str)
    )

    conect.commit()
    # узнаём id созданной строки
    task_id = cursor.lastrowid
    conect.close()

    return task_id


def  get_tasks(user_id, subject_id=None, only_active=True) -> list[dict]:
    """
    Возвращает список заданий пользователя.
  - subject_id=None — если передан, фильтрует по предмету, иначе все предметы
  - only_active=True — если True, возвращает только невыполненные (is_done=0)                                                                                               
  - Отсортировано по дедлайну от ближайшего к дальнему 
    """
    conect = get_connection()

    # запрос при условии что ubject_id=None 
    query = "SELECT id, subject_id, title, deadline, is_done FROM tasks WHERE user_id = ?"
    params = [user_id]

    # если subject_id задано
    if subject_id is not None:
        query += " AND subject_id = ?"
        params.append(subject_id)

    # если only_active=True
    if only_active:
        query += " AND is_done = 0"

    # сортировка по увеличению по дедлайну
    query += " ORDER BY deadline ASC"

    # отправляем запрос и получаем строки 
    rows = conect.execute(query, tuple(params)).fetchall()
    conect.close()

    return [
        {
            "id": r[0],
            "subject_id": r[1],
            "title": r[2],
            "deadline": r[3],
            "is_done": r[4]
        }
        for r in rows
    ]


def mark_done(user_id, task_id) -> bool:
    """
    Функция отмечает задание выполненым
    Возвращает: что-то изменено или нет
    """
    conect = get_connection()

    cursor = conect.execute(
        """
        UPDATE tasks
        SET is_done = 1
        WHERE id = ? AND user_id = ?
        """,
        (task_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0


def delete_task(user_id, task_id) -> bool: 
    """
    Функция удаляющее конкретное задание
    Возвращает: удалено ли что-то
    """
    conect = get_connection()

    # удаляем конкретное задание пользователя и смотрим сколько строк удалено, метаданные 
    cursor = conect.execute(
        "DELETE FROM tasks WHERE id = ? AND user_id = ?",
        (task_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0 

