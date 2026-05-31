from services import add_subject, get_subjects, delete_subject, update_subject_name, update_subject_note

from base_test import TestDatabase


class TestSubjects(TestDatabase):

    def test_add_subject(self):
        user_id = 1

        subject_id = add_subject(user_id, "Матан")

        subjects = get_subjects(user_id)

        self.assertEqual(len(subjects), 1)
        self.assertEqual(subjects[0]["id"], subject_id)
        self.assertEqual(subjects[0]["name"], "Матан")
        self.assertEqual(subjects[0]["note"], "")

    def test_add_subject_with_note(self):
        user_id = 1

        add_subject(user_id, "Матан", "ДЗ в classroom")

        subjects = get_subjects(user_id)

        self.assertEqual(subjects[0]["name"], "Матан")
        self.assertEqual(subjects[0]["note"], "ДЗ в classroom")

    def test_get_subjects_empty(self):
        subjects = get_subjects(1)

        self.assertEqual(subjects, [])

    def test_subjects_are_separated_by_user_id(self):
        add_subject(1, "Матан")
        add_subject(2, "Английский")

        subjects = get_subjects(1)

        self.assertEqual(len(subjects), 1)
        self.assertEqual(subjects[0]["name"], "Матан")

    def test_delete_subject(self):
        user_id = 1

        subject_id = add_subject(user_id, "Матан")

        result = delete_subject(user_id, subject_id)

        self.assertTrue(result)
        self.assertEqual(get_subjects(user_id), [])

    def test_delete_subject_wrong_user(self):
        subject_id = add_subject(1, "Матан")

        result = delete_subject(2, subject_id)

        self.assertFalse(result)
        self.assertEqual(len(get_subjects(1)), 1)

    def test_update_subject_name(self):
        user_id = 1

        subject_id = add_subject(user_id, "Матан")

        result = update_subject_name(user_id, subject_id, "Алгебра")

        subjects = get_subjects(user_id)

        self.assertTrue(result)
        self.assertEqual(subjects[0]["name"], "Алгебра")

    def test_update_subject_name_wrong_user(self):
        subject_id = add_subject(1, "Матан")

        result = update_subject_name(2, subject_id, "Алгебра")

        subjects = get_subjects(1)

        self.assertFalse(result)
        self.assertEqual(subjects[0]["name"], "Матан")

    def test_update_subject_note(self):
        user_id = 1

        subject_id = add_subject(user_id, "Матан")

        result = update_subject_note(user_id, subject_id, "Сложный предмет")

        subjects = get_subjects(user_id)

        self.assertTrue(result)
        self.assertEqual(subjects[0]["note"], "Сложный предмет")

    def test_update_subject_note_wrong_user(self):
        subject_id = add_subject(1, "Матан")

        result = update_subject_note(2, subject_id, "Заметка")

        subjects = get_subjects(1)

        self.assertFalse(result)
        self.assertEqual(subjects[0]["note"], "")