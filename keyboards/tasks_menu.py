from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

tasks_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить задание", callback_data="task_add")],
        [InlineKeyboardButton(text="📋 Список заданий", callback_data="task_list")],
        [InlineKeyboardButton(text="✅ Выполненные", callback_data="task_completed")],
        [InlineKeyboardButton(text="✅ Отметить выполненным", callback_data="task_done")],
        [InlineKeyboardButton(text="✏️ Редактировать задание", callback_data="task_edit")],
        [InlineKeyboardButton(text="🗑 Удалить задание", callback_data="task_delete")],
    ]
)
