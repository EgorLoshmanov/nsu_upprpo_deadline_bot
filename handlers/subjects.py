from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.subjects_menu import subjects_menu
from states.states import AddSubjectStates
from services.subject_service import add_subject, get_subjects, delete_subject

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


@router.callback_query(F.data == "subject_list")
async def subject_list(callback: CallbackQuery):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("У вас пока нет предметов.")
    else:
        lines = [f"{i + 1}. {s['name']}" for i, s in enumerate(subjects)]
        await callback.message.answer("📚 Ваши предметы:\n" + "\n".join(lines))
    await callback.answer()


@router.callback_query(F.data == "subject_delete")
async def subject_delete_start(callback: CallbackQuery):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("У вас пока нет предметов.")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=s["name"], callback_data=f"del_subj_{s['id']}")]
            for s in subjects
        ]
    )
    await callback.message.answer("Выберите предмет для удаления:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("del_subj_"))
async def subject_delete_confirm(callback: CallbackQuery):
    subject_id = int(callback.data.removeprefix("del_subj_"))
    deleted = delete_subject(user_id=callback.from_user.id, subject_id=subject_id)
    if deleted:
        await callback.message.answer("✅ Предмет удалён")
    else:
        await callback.message.answer("❌ Предмет не найден")
    await callback.answer()
