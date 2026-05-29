from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.types import Message

from keyboards.main_menu import main_menu

router = Router()


@router.message(StateFilter(None))
async def fallback_handler(message: Message):
    """
    Ловит любое сообщение, которое не подошло ни под одну команду, кнопку
    или шаг диалога. StateFilter(None) гарантирует, что обработчик НЕ
    срабатывает внутри FSM-диалогов (ввод названия, дедлайна и т.д.).
    """
    await message.answer(
        "🤔 Не понял сообщение. Воспользуйтесь меню ниже или командой /help.",
        reply_markup=main_menu,
    )
