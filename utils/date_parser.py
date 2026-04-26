# дает объект времени и временной сдвиг 
from datetime import date, timedelta 

ERROR_TEXT = "Не могу распознать дату. Попробуйте: 25.04, 25.04.2026, 25 апреля, завтра"

MONTHS = {
    "января": 1,
    "февраля": 2,
    "марта": 3,
    "апреля": 4,
    "мая": 5,
    "июня": 6,
    "июля": 7,
    "августа": 8,
    "сентября": 9,
    "октября": 10,
    "ноября": 11,
    "декабря": 12,
}

def parse_deadline(text: str) -> date:
    """
    Парсит строку дедлайна, введённую пользователем, в объект date.

    Поддерживаемые форматы:
    - "25.04"        → текущий год
    - "25.04.2026"   → с указанием года
    - "25 апреля"    → месяц словами
    - "завтра"
    - "послезавтра"

    Возвращает:
        datetime.date — нормализованную дату

    Исключения:
        ValueError — если формат не распознан или дата некорректна

    Зачем нужна:
        Пользователь вводит дату в свободной форме ("завтра", "25 апреля"),
        а функция приводит это к единому формату даты для хранения в БД
        (в виде ISO-строки через str(date)) и корректной сортировки.
    """
    
    # нормализуем текст
    text = text.strip().lower()

    # получаем сегодняшнее число (объект класса data.today)
    today = date.today()

    if (text == "завтра"):
        # возвращаем сдвинутую дату на 1 день вперед
        return today + timedelta(days=1)
    
    if (text == "послезавтра"):
        # возвращаем сдвинутую дату на 2 день вперед
        return today + timedelta(days=2)
    
    # разбиваем введенную дату по точке 25.4 -> [25, 4]
    parts = text.split(".")

    # проверка что в дате 2 или 3 части день месяц год
    if (len(parts) == 2 or len(parts) == 3):
        # обрабатываем ошибки 
        try:
            day = int(parts[0])
            month = int(parts[1])
            year = int(parts[2]) if len(parts) == 3 else today.year

            return date(year, month, day)
        
        # обработчик ловит только ошибки вызванные неправильным вводом данных (только такие ошибки мы ожидаем, если будут другие то это баг)
        except ValueError:
            # выводим ошибку
            raise ValueError(ERROR_TEXT)

    # разбиваем по пробелам 25  3 -> [25, 3]
    parts = text.split()

    if (len(parts) == 2):

        try:
            day = int(parts[0])
            month = MONTHS[parts[1]]

            return date(today.year, month, day)
        
        except (ValueError, KeyError):

            raise ValueError(ERROR_TEXT)
    
    # ну на случай если введут "AAAAAA"
    raise ValueError(ERROR_TEXT)
