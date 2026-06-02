from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.tasks_menu import tasks_menu
from states.states import AddTaskStates, EditTaskStates
from .filters import is_dialog_input
from services.subject_service import get_subjects
from services.tasks_service import (
    add_task,
    get_tasks,
    mark_done,
    delete_task,
    update_task_title,
    update_task_deadline,
    update_task_note,
)
from utils import parse_deadline, answer_long

from datetime import date

router = Router()

NOTE_PROMPT = (
    "Введите заметку к заданию (ссылка, пояснение) "
    "или отправьте «-», чтобы пропустить:"
)


@router.message(Command("add"))
@router.message(F.text == "📝 Задания")
async def tasks_handler(message: Message, state: FSMContext):
    await state.clear()
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


@router.message(AddTaskStates.waiting_title, is_dialog_input)
async def task_add_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите дедлайн (например: 25.04, завтра, 5 мая):")
    await state.set_state(AddTaskStates.waiting_deadline)


@router.message(AddTaskStates.waiting_deadline, is_dialog_input)
async def task_add_deadline(message: Message, state: FSMContext):
    try:
        deadline = parse_deadline(message.text)
    except ValueError as e:
        await message.answer(f"❌ {e}\nПопробуйте ещё раз:")
        return
    await state.update_data(deadline=message.text)

    if deadline < date.today():
        keyboard = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(text="✅ Всё равно добавить", callback_data="past_ok")],
                [InlineKeyboardButton(text="✏️ Ввести другую дату", callback_data="past_change")],
            ]
        )
        await message.answer(
            f"⚠️ Дата {deadline} уже прошла. Всё равно добавить задание?",
            reply_markup=keyboard,
        )
        await state.set_state(AddTaskStates.confirm_past_deadline)
        return

    await message.answer(NOTE_PROMPT)
    await state.set_state(AddTaskStates.waiting_note)


@router.callback_query(F.data == "past_ok", AddTaskStates.confirm_past_deadline)
async def task_add_past_ok(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(NOTE_PROMPT)
    await state.set_state(AddTaskStates.waiting_note)
    await callback.answer()


@router.callback_query(F.data == "past_change", AddTaskStates.confirm_past_deadline)
async def task_add_past_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите дедлайн (например: 25.04, завтра, 5 мая):")
    await state.set_state(AddTaskStates.waiting_deadline)
    await callback.answer()


@router.message(AddTaskStates.waiting_note, is_dialog_input)
async def task_add_note(message: Message, state: FSMContext):
    data = await state.get_data()
    note = "" if message.text.strip() == "-" else message.text
    add_task(
        user_id=message.from_user.id,
        subject_id=data["subject_id"],
        title=data["title"],
        deadline_str=data["deadline"],
        note=note,
    )
    await state.clear()
    await message.answer("✅ Задание добавлено!")


@router.message(Command("list"))
@router.callback_query(F.data == "task_list")
async def task_list(event: Message | CallbackQuery):
    user_id = event.from_user.id
    tasks = get_tasks(user_id=user_id, only_active=True)

    if not tasks:
        text = "Активных заданий нет. Добавьте через /add."
    else:
        subjects = {s["id"]: s["name"] for s in get_subjects(user_id=user_id)}
        lines = []
        for t in tasks:
            subject_name = subjects.get(t["subject_id"], "—")
            line = f"📌 {t['title']}\n📚 {subject_name}\n📅 Дедлайн: {t['deadline']}"
            if t["note"]:
                line += f"\n📝 {t['note']}"
            lines.append(line)
        text = "\n\n".join(lines)

    if isinstance(event, CallbackQuery):
        await answer_long(event.message, text)
        await event.answer()
    else:
        await answer_long(event, text)


@router.callback_query(F.data == "task_by_subject")
async def task_by_subject_start(callback: CallbackQuery):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("Сначала добавьте предмет через /subjects.")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=s["name"], callback_data=f"tasks_subj_{s['id']}")]
            for s in subjects
        ]
    )
    await callback.message.answer("Выберите предмет:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("tasks_subj_"))
async def task_by_subject_list(callback: CallbackQuery):
    subject_id = int(callback.data.removeprefix("tasks_subj_"))
    user_id = callback.from_user.id
    tasks = get_tasks(user_id=user_id, subject_id=subject_id, only_active=True)

    subjects = {s["id"]: s["name"] for s in get_subjects(user_id=user_id)}
    subject_name = subjects.get(subject_id, "—")

    if not tasks:
        text = f"📚 {subject_name}: активных заданий нет."
    else:
        lines = []
        for t in tasks:
            line = f"📌 {t['title']}\n📅 Дедлайн: {t['deadline']}"
            if t["note"]:
                line += f"\n📝 {t['note']}"
            lines.append(line)
        text = f"📚 {subject_name}:\n\n" + "\n\n".join(lines)

    await answer_long(callback.message, text)
    await callback.answer()


@router.message(Command("completed"))
@router.callback_query(F.data == "task_completed")
async def task_completed_list(event: Message | CallbackQuery):
    user_id = event.from_user.id
    tasks = [t for t in get_tasks(user_id=user_id, only_active=False) if t["is_done"]]

    if not tasks:
        text = "Выполненных заданий нет."
    else:
        subjects = {s["id"]: s["name"] for s in get_subjects(user_id=user_id)}
        lines = []
        for t in tasks:
            subject_name = subjects.get(t["subject_id"], "—")
            line = f"✅ {t['title']}\n📚 {subject_name}\n📅 Дедлайн: {t['deadline']}"
            if t["note"]:
                line += f"\n📝 {t['note']}"
            lines.append(line)
        text = "✅ Выполненные задания:\n\n" + "\n\n".join(lines)

    if isinstance(event, CallbackQuery):
        await answer_long(event.message, text)
        await event.answer()
    else:
        await answer_long(event, text)


@router.message(Command("done"))
@router.callback_query(F.data == "task_done")
async def task_done_start(event: Message | CallbackQuery):
    user_id = event.from_user.id
    tasks = get_tasks(user_id=user_id, only_active=True)

    if not tasks:
        text = "Активных заданий нет."
        if isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()
        else:
            await event.answer(text)
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=t["title"], callback_data=f"done_{t['id']}")]
            for t in tasks
        ]
    )
    text = "Выберите выполненное задание:"
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("done_"))
async def task_done_confirm(callback: CallbackQuery):
    task_id = int(callback.data.removeprefix("done_"))
    if mark_done(user_id=callback.from_user.id, task_id=task_id):
        await callback.message.answer("✅ Задание отмечено выполненным")
    else:
        await callback.message.answer("❌ Задание не найдено")
    await callback.answer()


@router.message(Command("delete"))
@router.callback_query(F.data == "task_delete")
async def task_delete_start(event: Message | CallbackQuery):
    user_id = event.from_user.id
    tasks = get_tasks(user_id=user_id, only_active=False)

    if not tasks:
        text = "Заданий нет."
        if isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()
        else:
            await event.answer(text)
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=("✅ " if t["is_done"] else "") + t["title"],
                callback_data=f"del_task_{t['id']}",
            )]
            for t in tasks
        ]
    )
    text = "Выберите задание для удаления:"
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("del_task_"))
async def task_delete_confirm(callback: CallbackQuery):
    task_id = int(callback.data.removeprefix("del_task_"))
    if delete_task(user_id=callback.from_user.id, task_id=task_id):
        await callback.message.answer("🗑 Задание удалено")
    else:
        await callback.message.answer("❌ Задание не найдено")
    await callback.answer()


EDIT_FIELD_PROMPTS = {
    "title": "Введите новое название задания:",
    "deadline": "Введите новый дедлайн (например: 25.04, завтра, 5 мая):",
    "note": "Введите новую заметку (или «-», чтобы очистить):",
}


@router.message(Command("edit"))
@router.callback_query(F.data == "task_edit")
async def task_edit_start(event: Message | CallbackQuery):
    user_id = event.from_user.id
    tasks = get_tasks(user_id=user_id, only_active=False)

    if not tasks:
        text = "Заданий нет."
        if isinstance(event, CallbackQuery):
            await event.message.answer(text)
            await event.answer()
        else:
            await event.answer(text)
        return

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=("✅ " if t["is_done"] else "") + t["title"],
                callback_data=f"edit_task_{t['id']}",
            )]
            for t in tasks
        ]
    )
    text = "Выберите задание для редактирования:"
    if isinstance(event, CallbackQuery):
        await event.message.answer(text, reply_markup=keyboard)
        await event.answer()
    else:
        await event.answer(text, reply_markup=keyboard)


@router.callback_query(F.data.startswith("edit_task_"))
async def task_edit_choose_field(callback: CallbackQuery):
    task_id = int(callback.data.removeprefix("edit_task_"))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Название", callback_data=f"ef_title_{task_id}")],
            [InlineKeyboardButton(text="📅 Дедлайн", callback_data=f"ef_deadline_{task_id}")],
            [InlineKeyboardButton(text="🗒 Заметка", callback_data=f"ef_note_{task_id}")],
        ]
    )
    await callback.message.answer("Что изменить?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("ef_"))
async def task_edit_field_selected(callback: CallbackQuery, state: FSMContext):
    field, task_id = callback.data.removeprefix("ef_").rsplit("_", 1)
    await state.update_data(task_id=int(task_id), field=field)
    await callback.message.answer(EDIT_FIELD_PROMPTS[field])
    await state.set_state(EditTaskStates.waiting_value)
    await callback.answer()


@router.message(EditTaskStates.waiting_value, is_dialog_input)
async def task_edit_apply(message: Message, state: FSMContext):
    data = await state.get_data()
    task_id = data["task_id"]
    field = data["field"]
    user_id = message.from_user.id

    if field == "deadline":
        try:
            deadline = parse_deadline(message.text)
        except ValueError as e:
            await message.answer(f"❌ {e}\nПопробуйте ещё раз:")
            return
        if deadline < date.today():
            await state.update_data(new_value=message.text)
            keyboard = InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(text="✅ Всё равно сохранить", callback_data="edit_past_ok")],
                    [InlineKeyboardButton(text="✏️ Ввести другую дату", callback_data="edit_past_change")],
                ]
            )
            await message.answer(
                f"⚠️ Дата {deadline} уже прошла. Всё равно сохранить?",
                reply_markup=keyboard,
            )
            await state.set_state(EditTaskStates.confirm_past_deadline)
            return
        ok = update_task_deadline(task_id, user_id, message.text)
    elif field == "title":
        ok = update_task_title(task_id, user_id, message.text)
    else:
        note = "" if message.text.strip() == "-" else message.text
        ok = update_task_note(task_id, user_id, note)

    await state.clear()
    await message.answer("✅ Задание обновлено" if ok else "❌ Задание не найдено")


@router.callback_query(F.data == "edit_past_ok", EditTaskStates.confirm_past_deadline)
async def task_edit_past_ok(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    ok = update_task_deadline(data["task_id"], callback.from_user.id, data["new_value"])
    await state.clear()
    await callback.message.answer("✅ Задание обновлено" if ok else "❌ Задание не найдено")
    await callback.answer()


@router.callback_query(F.data == "edit_past_change", EditTaskStates.confirm_past_deadline)
async def task_edit_past_change(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(EDIT_FIELD_PROMPTS["deadline"])
    await state.set_state(EditTaskStates.waiting_value)
    await callback.answer()
