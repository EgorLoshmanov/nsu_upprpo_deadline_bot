from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

tasks_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить задание", callback_data="task_add")],
        [InlineKeyboardButton(text="📋 Список заданий", callback_data="task_list")],
        [InlineKeyboardButton(text="✅ Отметить выполненным", callback_data="task_done")],
    ]
)
