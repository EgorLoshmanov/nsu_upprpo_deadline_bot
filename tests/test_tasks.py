from services import add_task, get_tasks, mark_done, delete_task, get_tasks_due_in, get_tasks_by_deadline

from services import update_task_title, update_task_deadline, update_task_note, delete_old_tasks, delete_old_tasks_completed

from services import add_subject

from datetime import date, timedelta


from base_test import TestDatabase



class TestTasks(TestDatabase):

    def test_add_task(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        task_id = add_task(user_id, subject_id, "ДЗ 1", "25.04.2026", "решить задачи")

        tasks = get_tasks(user_id)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], task_id)
        self.assertEqual(tasks[0]["subject_id"], subject_id)
        self.assertEqual(tasks[0]["title"], "ДЗ 1")
        self.assertEqual(tasks[0]["deadline"], "2026-04-25")
        self.assertEqual(tasks[0]["is_done"], 0)
        self.assertEqual(tasks[0]["note"], "решить задачи")

    def test_get_tasks_empty(self):
        tasks = get_tasks(1)

        self.assertEqual(tasks, [])

    def test_tasks_sorted_by_deadline(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        add_task(user_id, subject_id, "Поздняя задача", "30.04.2026")
        add_task(user_id, subject_id, "Ранняя задача", "20.04.2026")

        tasks = get_tasks(user_id)

        self.assertEqual(tasks[0]["title"], "Ранняя задача")
        self.assertEqual(tasks[1]["title"], "Поздняя задача")

    def test_filter_tasks_by_subject(self):
        user_id = 1
        math_id = add_subject(user_id, "Матан")
        english_id = add_subject(user_id, "Английский")

        add_task(user_id, math_id, "ДЗ по матану", "20.04.2026")
        add_task(user_id, english_id, "Эссе", "21.04.2026")

        tasks = get_tasks(user_id, subject_id=math_id)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "ДЗ по матану")

    def test_tasks_are_separated_by_user_id(self):
        subject_1 = add_subject(1, "Матан")
        subject_2 = add_subject(2, "Английский")

        add_task(1, subject_1, "ДЗ 1", "20.04.2026")
        add_task(2, subject_2, "Essay", "21.04.2026")

        tasks = get_tasks(1)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "ДЗ 1")

    def test_mark_done(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")
        task_id = add_task(user_id, subject_id, "ДЗ 1", "25.04.2026")

        result = mark_done(user_id, task_id)

        active_tasks = get_tasks(user_id)
        all_tasks = get_tasks(user_id, only_active=False)

        self.assertTrue(result)
        self.assertEqual(active_tasks, [])
        self.assertEqual(len(all_tasks), 1)
        self.assertEqual(all_tasks[0]["is_done"], 1)

    def test_mark_done_wrong_user(self):
        subject_id = add_subject(1, "Матан")
        task_id = add_task(1, subject_id, "ДЗ 1", "25.04.2026")

        result = mark_done(2, task_id)

        tasks = get_tasks(1, only_active=False)

        self.assertFalse(result)
        self.assertEqual(tasks[0]["is_done"], 0)

    def test_delete_task(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")
        task_id = add_task(user_id, subject_id, "ДЗ 1", "25.04.2026")

        result = delete_task(user_id, task_id)

        self.assertTrue(result)
        self.assertEqual(get_tasks(user_id), [])

    def test_delete_task_wrong_user(self):
        subject_id = add_subject(1, "Матан")
        task_id = add_task(1, subject_id, "ДЗ 1", "25.04.2026")

        result = delete_task(2, task_id)

        self.assertFalse(result)
        self.assertEqual(len(get_tasks(1)), 1)

    def test_get_tasks_due_in(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        today = date.today()

        task_soon = add_task(
            user_id,
            subject_id,
            "Скоро",
            (today + timedelta(days=2)).strftime("%d.%m.%Y"),
        )

        add_task(
            user_id,
            subject_id,
            "Поздно",
            (today + timedelta(days=10)).strftime("%d.%m.%Y"),
        )

        tasks = get_tasks_due_in(user_id, 7)

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], task_soon)

    def test_get_tasks_due_in_ignores_done_tasks(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        today = date.today()

        task_id = add_task(
            user_id,
            subject_id,
            "Скоро, но выполнено",
            (today + timedelta(days=2)).strftime("%d.%m.%Y"),
        )

        mark_done(user_id, task_id)

        tasks = get_tasks_due_in(user_id, 7)

        self.assertEqual(tasks, [])

    def test_get_tasks_by_deadline(self):
        deadline = date.today() + timedelta(days=1)

        subject_1 = add_subject(1, "Матан")
        subject_2 = add_subject(2, "Английский")

        task_1 = add_task(1, subject_1, "ДЗ 1", deadline.strftime("%d.%m.%Y"))
        task_2 = add_task(2, subject_2, "Essay", deadline.strftime("%d.%m.%Y"))

        tasks = get_tasks_by_deadline(deadline)

        self.assertEqual({task["id"] for task in tasks}, {task_1, task_2})
        self.assertEqual({task["user_id"] for task in tasks}, {1, 2})

    def test_update_task_title(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")
        task_id = add_task(user_id, subject_id, "Старое название", "25.04.2026")

        result = update_task_title(task_id, user_id, "Новое название")

        task = get_tasks(user_id)[0]

        self.assertTrue(result)
        self.assertEqual(task["title"], "Новое название")

    def test_update_task_deadline(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")
        task_id = add_task(user_id, subject_id, "ДЗ 1", "25.04.2026")

        result = update_task_deadline(task_id, user_id, "26.04.2026")

        task = get_tasks(user_id)[0]

        self.assertTrue(result)
        self.assertEqual(task["deadline"], "2026-04-26")

    def test_update_task_note(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")
        task_id = add_task(user_id, subject_id, "ДЗ 1", "25.04.2026")

        result = update_task_note(task_id, user_id, "новая заметка")

        task = get_tasks(user_id)[0]

        self.assertTrue(result)
        self.assertEqual(task["note"], "новая заметка")

    def test_update_task_wrong_user(self):
        subject_id = add_subject(1, "Матан")
        task_id = add_task(1, subject_id, "ДЗ 1", "25.04.2026")

        result_title = update_task_title(task_id, 2, "Взлом")
        result_deadline = update_task_deadline(task_id, 2, "26.04.2026")
        result_note = update_task_note(task_id, 2, "Взлом")

        task = get_tasks(1)[0]

        self.assertFalse(result_title)
        self.assertFalse(result_deadline)
        self.assertFalse(result_note)
        self.assertEqual(task["title"], "ДЗ 1")
        self.assertEqual(task["deadline"], "2026-04-25")
        self.assertEqual(task["note"], "")

    def test_delete_old_tasks(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        add_task(user_id, subject_id, "Старая задача", "01.01.2020")
        add_task(user_id, subject_id, "Новая задача", "01.01.2099")

        deleted_count = delete_old_tasks(days=12)

        tasks = get_tasks(user_id)

        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Новая задача")

    def test_delete_old_tasks_completed(self):
        user_id = 1
        subject_id = add_subject(user_id, "Матан")

        old_task = add_task(user_id, subject_id, "Старая выполненная", "01.01.2020")
        new_task = add_task(user_id, subject_id, "Новая выполненная", "01.01.2099")

        mark_done(user_id, old_task)
        mark_done(user_id, new_task)

        import db.database as database

        conn = database.get_connection()
        conn.execute(
            "UPDATE tasks SET done_at = ? WHERE id = ?",
            ("2020-01-01", old_task),
        )
        conn.commit()
        conn.close()

        deleted_count = delete_old_tasks_completed(days=30)

        tasks = get_tasks(user_id, only_active=False)

        self.assertEqual(deleted_count, 1)
        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["title"], "Новая выполненная")