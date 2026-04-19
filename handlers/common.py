from aiogram import Router, F
from aiogram.filters import CommandStart, Command
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
    await message.answer("<Пояснение работы бота>")


@router.message(F.text == "📚 Предметы")
async def subjects_stub(message: Message):
    await message.answer("В разработке...")


@router.message(F.text == "📝 Задания")
async def tasks_stub(message: Message):
    await message.answer("В разработке...")


@router.message(F.text == "📅 Ближайшие дедлайны")
async def deadlines_stub(message: Message):
    await message.answer("В разработке...")


@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    await help_handler(message)
