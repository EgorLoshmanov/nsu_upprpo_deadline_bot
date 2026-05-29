from db.database import get_connection

from utils import parse_deadline

from datetime import date, timedelta



def add_task(user_id, subject_id, title, deadline_str, note: str = "") -> int:
    """
    Добавляет новое задание в таблицу tasks.

    Параметры:
        user_id — id пользователя Telegram
        subject_id — id предмета, к которому относится задание
        title — название задания
        deadline_str — дедлайн в виде строки, введённой пользователем
        note — заметка к заданию: ссылка, пояснение, условие и т.д.
    Возвращает:
        id созданного задания
    Особенность:
        deadline_str перед сохранением парсится через parse_deadline()
        и сохраняется в БД в нормализованном ISO-формате YYYY-MM-DD.
    """

    conect = get_connection()

    deadline_str = str(parse_deadline(deadline_str))

    cursor = conect.execute(
        "INSERT INTO tasks (user_id, subject_id, title, deadline, note) VALUES (?, ?, ?, ?, ?)", 
        (user_id, subject_id, title, deadline_str, note)
    )

    conect.commit()
    # узнаём id созданной строки
    task_id = cursor.lastrowid
    conect.close()

    return task_id


def get_tasks(user_id, subject_id=None, only_active=True) -> list[dict]:
    """
    Возвращает список заданий пользователя.

    Параметры:
        user_id — id пользователя Telegram
        subject_id — если передан, возвращаются задачи только этого предмета
        only_active — если True, возвращаются только невыполненные задачи
    Возвращает:
        список словарей с полями:
        id, subject_id, title, deadline, is_done, note
    Особенность:
        задачи отсортированы по дедлайну от ближайшего к дальнему.
    """
    
    conect = get_connection()

    # запрос при условии что ubject_id=None 
    query = "SELECT id, subject_id, title, deadline, is_done, note FROM tasks WHERE user_id = ?"
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
            "is_done": r[4],
            "note": r[5],
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
        "UPDATE tasks SET is_done = 1, done_at = ? WHERE id = ? AND user_id = ?",
        (str(date.today()), task_id, user_id)
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


def get_tasks_due_in(user_id: int, days: int) -> list[dict]:
    """
    Возвращает задачи пользователя с дедлайном в ближайшие N дней.

    Параметры:
        user_id — id пользователя Telegram
        days — количество дней вперёд от сегодняшней даты
    Возвращает:
        список словарей с полями:
        id, subject_id, title, deadline, is_done, note
    Особенность:
        возвращаются только невыполненные задачи.
    """

    conect = get_connection()

    today = date.today()
    end_date = today + timedelta(days=days)

    rows = conect.execute(
        """
        SELECT id, subject_id, title, deadline, is_done, note
        FROM tasks
        WHERE user_id = ?
          AND is_done = 0
          AND deadline BETWEEN ? AND ?
        ORDER BY deadline ASC
        """,
        (user_id, str(today), str(end_date))
    ).fetchall()

    conect.close()

    return [
        {
            "id": r[0],
            "subject_id": r[1],
            "title": r[2],
            "deadline": r[3],
            "is_done": r[4],
            "note": r[5]
        }
        for r in rows
    ]


# для уведомлений о дедлайне
def get_tasks_by_deadline(deadline: date) -> list[dict]:
    conect = get_connection()

    rows = conect.execute(
        "SELECT id, user_id, title, deadline FROM tasks WHERE is_done = 0 AND deadline = ?",
        (str(deadline),)
    ).fetchall()

    conect.close()

    return [
        {
            "id": r[0],
            "user_id": r[1],
            "title": r[2],
            "deadline": r[3],
        }
        for r in rows
    ]

def update_task_title(task_id: int, user_id: int, title: str):
    """
    Обновляет название конкретного задания пользователя.

    Параметры:
        user_id — id пользователя Telegram
        task_id — id задания
        title — новое название задания
    Возвращает:
        True, если задание найдено и обновлено
        False, если задание не найдено
    """
     
    conect = get_connection()

    cursor = conect.execute(
        "UPDATE tasks SET title = ? WHERE id = ? AND user_id = ?",
        (title, task_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0


def update_task_deadline(task_id: int, user_id: int, deadline_str: str):
    """
    Обновляет дедлайн конкретного задания пользователя.

    Параметры:
        user_id — id пользователя Telegram
        task_id — id задания
        deadline_str — новая дата дедлайна в виде строки
    Возвращает:
        True, если задание найдено и обновлено
        False, если задание не найдено
    Особенность:
        deadline_str перед сохранением парсится через parse_deadline()
        и сохраняется в БД в формате YYYY-MM-DD.
    """

    conect = get_connection()

    deadline = str(parse_deadline(deadline_str))

    cursor = conect.execute(
        "UPDATE tasks SET deadline = ? WHERE id = ? AND user_id = ?",
        (deadline, task_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0


def update_task_note(task_id: int, user_id: int, note: str):
    """
    Обновляет заметку конкретного задания пользователя.

    Параметры:
        user_id — id пользователя Telegram
        task_id — id задания
        note — новая заметка к заданию
    Возвращает:
        True, если задание найдено и обновлено
        False, если задание не найдено
    """

    conect = get_connection()

    cursor = conect.execute(
        "UPDATE tasks SET note = ? WHERE id = ? AND user_id = ?",
        (note, task_id, user_id)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount > 0


def delete_old_tasks(days: int = 12) -> int:
    """
    Удаляет старые невыполненные задачи

    Параметры:
        days — через сколько дней после дедлайна удалять задачу
    Возвращает:
        количество удалённых задач
    """

    conect = get_connection()

    border_date = date.today() - timedelta(days=days)

    cursor = conect.execute(
        "DELETE FROM tasks WHERE is_done = 0 AND deadline <= ?",
        (str(border_date),)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount

def delete_old_tasks_completed(days: int = 30) -> int:
    """
    Удаляет старые выполненные задачи

    Параметры:
        days — через сколько дней после отметки выполнения удалять задачу
    Возвращает:
        количество удалённых задач
    Особенность:
        отсчёт идёт от done_at (даты отметки выполнения). Для задач,
        выполненных до появления поля done_at, отсчёт идёт от дедлайна.
    """

    conect = get_connection()

    border_date = date.today() - timedelta(days=days)

    cursor = conect.execute(
        "DELETE FROM tasks WHERE is_done = 1 AND COALESCE(done_at, deadline) <= ?",
        (str(border_date),)
    )

    conect.commit()
    conect.close()

    return cursor.rowcount