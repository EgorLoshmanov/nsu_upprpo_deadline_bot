from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

subjects_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить предмет", callback_data="subject_add")],
    ]
)
