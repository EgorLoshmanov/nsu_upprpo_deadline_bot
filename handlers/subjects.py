from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from keyboards.subjects_menu import subjects_menu
from states.states import AddSubjectStates
from services.subject_service import add_subject

router = Router()


@router.message(Command("subjects"))
@router.message(F.text == "📚 Предметы")
async def subjects_handler(message: Message):
    await message.answer("📚 Управление предметами:", reply_markup=subjects_menu)


@router.callback_query(F.data == "subject_add")
async def subject_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название предмета:")
    await state.set_state(AddSubjectStates.waiting_name)
    await callback.answer()


@router.message(AddSubjectStates.waiting_name)
async def subject_add_finish(message: Message, state: FSMContext):
    add_subject(user_id=message.from_user.id, name=message.text)
    await state.clear()
    await message.answer("✅ Предмет добавлен")
