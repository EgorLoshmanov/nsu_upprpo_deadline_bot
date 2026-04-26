from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

subjects_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить предмет", callback_data="subject_add")],
        [InlineKeyboardButton(text="📋 Список предметов", callback_data="subject_list")],
        [InlineKeyboardButton(text="🗑 Удалить предмет",  callback_data="subject_delete")],
    ]
)
