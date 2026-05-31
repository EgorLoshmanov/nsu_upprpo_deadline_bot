import os
import unittest

import db.database as database
from db.init_db import init_db

# запуск тестов
# python -m unittest discover -s tests -v

# -m      - запуск модуля как программы
# unittest - встроенная библиотека тестирования
# discover - автоматический поиск тестов
# -s tests - искать тесты в папке tests
# -v      - подробный вывод результатов


class TestDatabase(unittest.TestCase):

    # меняем путь к тестовой бд
    def setUp(self):
        database.DB_PATH = "test.db"

        # если есть файл test.db то удаляем его
        if os.path.exists("test.db"):
            os.remove("test.db")

        # создаем таблицу
        init_db()

    def tearDown(self):
        # если есть файл test.db то удаляем его
        if os.path.exists("test.db"):
            os.remove("test.db")

    # меняем путь к бд проекта
    def tearDown(self):
        if os.path.exists("test.db"):
            os.remove("test.db")

        database.DB_PATH = "deadlines.db"