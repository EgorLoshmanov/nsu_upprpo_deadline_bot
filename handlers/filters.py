from aiogram.types import Message

from keyboards.main_menu import MENU_BUTTONS


def is_dialog_input(message: Message) -> bool:
    """
    True, если сообщение — обычный текстовый ввод диалога, а не команда
    или кнопка главного меню. Используется как фильтр на FSM-шагах, чтобы
    навигация (кнопки/команды) не воспринималась как ввод и обрабатывалась
    своими хендлерами (которые сбрасывают состояние).
    """
    text = message.text
    return bool(text) and not text.startswith("/") and text not in MENU_BUTTONS
