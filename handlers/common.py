from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main_menu import main_menu

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer(
        f"👋 Привет, {message.from_user.first_name}! Я помогу отслеживать учебные дедлайны.\n"
        "Выбери действие:",
        reply_markup=main_menu,
    )


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer(
        "📖 Команды бота:\n"
        "/start — главное меню\n"
        "/add — добавить задание\n"
        "/list — список заданий\n"
        "/subjects — управление предметами\n"
        "/done — отметить задание выполненным\n"
        "/help — это сообщение"
    )


@router.message(Command("cancel"))
async def cancel_handler(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("Нет активного действия для отмены.")
        return
    await state.clear()
    await message.answer("❌ Действие отменено.", reply_markup=main_menu)



@router.message(F.text == "📅 Ближайшие дедлайны")
async def deadlines_stub(message: Message):
    await message.answer("В разработке...")


@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    await help_handler(message)
