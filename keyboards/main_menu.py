from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Предметы"), KeyboardButton(text="📝 Задания")],
        [KeyboardButton(text="📅 Ближайшие дедлайны"), KeyboardButton(text="❓ Помощь")],
    ],
    resize_keyboard=True,
)
