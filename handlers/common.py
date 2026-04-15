from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

router = Router()


@router.message(CommandStart())
async def start(message: Message):
    await message.answer("<Приветствие пользователя>")


@router.message(Command("help"))
async def help_handler(message: Message):
    await message.answer("<Пояснение работы бота>")
