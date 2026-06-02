from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📚 Предметы"), KeyboardButton(text="📝 Задания")],
        [KeyboardButton(text="📅 Ближайшие дедлайны"), KeyboardButton(text="❓ Помощь")],
    ],
    resize_keyboard=True,
)

# тексты кнопок главного меню — используются, чтобы FSM-диалоги не «съедали»
# нажатие на кнопку меню как обычный ввод
MENU_BUTTONS = {"📚 Предметы", "📝 Задания", "📅 Ближайшие дедлайны", "❓ Помощь"}
