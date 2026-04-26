from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.tasks_menu import tasks_menu
from states.states import AddTaskStates
from services.subject_service import get_subjects
from services.tasks_service import add_task

router = Router()


@router.message(Command("add"))
@router.message(F.text == "📝 Задания")
async def tasks_handler(message: Message):
    await message.answer("📝 Управление заданиями:", reply_markup=tasks_menu)


@router.callback_query(F.data == "task_add")
async def task_add_start(callback: CallbackQuery, state: FSMContext):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("Сначала добавьте предмет через /subjects.")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=s["name"], callback_data=f"add_task_subj_{s['id']}")]
            for s in subjects
        ]
    )
    await callback.message.answer("Выберите предмет:", reply_markup=keyboard)
    await state.set_state(AddTaskStates.waiting_subject)
    await callback.answer()


@router.callback_query(F.data.startswith("add_task_subj_"), AddTaskStates.waiting_subject)
async def task_add_subject(callback: CallbackQuery, state: FSMContext):
    subject_id = int(callback.data.removeprefix("add_task_subj_"))
    await state.update_data(subject_id=subject_id)
    await callback.message.answer("Введите название задания:")
    await state.set_state(AddTaskStates.waiting_title)
    await callback.answer()


@router.message(AddTaskStates.waiting_title)
async def task_add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите дедлайн (например: 25.04, завтра, 5 мая):")
    await state.set_state(AddTaskStates.waiting_deadline)


@router.message(AddTaskStates.waiting_deadline)
async def task_add_deadline(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        add_task(
            user_id=message.from_user.id,
            subject_id=data["subject_id"],
            title=data["title"],
            deadline_str=message.text,
        )
    except ValueError as e:
        await message.answer(f"❌ {e}\nПопробуйте ещё раз:")
        return
    await state.clear()
    await message.answer("✅ Задание добавлено!")


@router.callback_query(F.data == "task_list")
async def task_list_stub(callback: CallbackQuery):
    await callback.message.answer("В разработке...")
    await callback.answer()


@router.callback_query(F.data == "task_done")
async def task_done_stub(callback: CallbackQuery):
    await callback.message.answer("В разработке...")
    await callback.answer()
