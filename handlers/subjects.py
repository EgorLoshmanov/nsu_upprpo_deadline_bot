from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.subjects_menu import subjects_menu
from states.states import AddSubjectStates, EditSubjectStates
from .filters import is_dialog_input
from services.subject_service import (
    add_subject,
    get_subjects,
    delete_subject,
    update_subject_name,
    update_subject_note,
)

router = Router()


def _name_taken(user_id: int, name: str, exclude_id: int | None = None) -> bool:
    """
    Проверяет, есть ли у пользователя предмет с таким же именем
    (без учёта регистра и крайних пробелов). exclude_id позволяет
    исключить сам редактируемый предмет (чтобы не считать его дубликатом).
    """
    target = name.strip().lower()
    for s in get_subjects(user_id):
        if exclude_id is not None and s["id"] == exclude_id:
            continue
        if s["name"].strip().lower() == target:
            return True
    return False


@router.message(Command("subjects"))
@router.message(F.text == "📚 Предметы")
async def subjects_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("📚 Управление предметами:", reply_markup=subjects_menu)


@router.callback_query(F.data == "subject_add")
async def subject_add_start(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите название предмета:")
    await state.set_state(AddSubjectStates.waiting_name)
    await callback.answer()


@router.message(AddSubjectStates.waiting_name, is_dialog_input)
async def subject_add_name(message: Message, state: FSMContext):
    if _name_taken(message.from_user.id, message.text):
        await state.clear()
        await message.answer("❌ Такой предмет уже есть.")
        return
    await state.update_data(name=message.text)
    await message.answer(
        "Введите заметку к предмету (ссылка, пояснение) "
        "или отправьте «-», чтобы пропустить:"
    )
    await state.set_state(AddSubjectStates.waiting_note)


@router.message(AddSubjectStates.waiting_note, is_dialog_input)
async def subject_add_finish(message: Message, state: FSMContext):
    data = await state.get_data()
    note = "" if message.text.strip() == "-" else message.text
    add_subject(user_id=message.from_user.id, name=data["name"], note=note)
    await state.clear()
    await message.answer("✅ Предмет добавлен")


@router.callback_query(F.data == "subject_list")
async def subject_list(callback: CallbackQuery):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("У вас пока нет предметов.")
    else:
        lines = []
        for i, s in enumerate(subjects):
            line = f"{i + 1}. {s['name']}"
            if s["note"]:
                line += f"\n   📝 {s['note']}"
            lines.append(line)
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


EDIT_FIELD_PROMPTS = {
    "name": "Введите новое название предмета:",
    "note": "Введите новую заметку (или «-», чтобы очистить):",
}


@router.callback_query(F.data == "subject_edit")
async def subject_edit_start(callback: CallbackQuery):
    subjects = get_subjects(user_id=callback.from_user.id)
    if not subjects:
        await callback.message.answer("У вас пока нет предметов.")
        await callback.answer()
        return
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text=s["name"], callback_data=f"edit_subj_{s['id']}")]
            for s in subjects
        ]
    )
    await callback.message.answer("Выберите предмет для редактирования:", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_subj_"))
async def subject_edit_choose_field(callback: CallbackQuery):
    subject_id = int(callback.data.removeprefix("edit_subj_"))
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="📝 Название", callback_data=f"sf_name_{subject_id}")],
            [InlineKeyboardButton(text="🗒 Заметка", callback_data=f"sf_note_{subject_id}")],
        ]
    )
    await callback.message.answer("Что изменить?", reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("sf_"))
async def subject_edit_field_selected(callback: CallbackQuery, state: FSMContext):
    field, subject_id = callback.data.removeprefix("sf_").rsplit("_", 1)
    await state.update_data(subject_id=int(subject_id), field=field)
    await callback.message.answer(EDIT_FIELD_PROMPTS[field])
    await state.set_state(EditSubjectStates.waiting_value)
    await callback.answer()


@router.message(EditSubjectStates.waiting_value, is_dialog_input)
async def subject_edit_apply(message: Message, state: FSMContext):
    data = await state.get_data()
    subject_id = data["subject_id"]
    field = data["field"]
    user_id = message.from_user.id

    if field == "name":
        if _name_taken(user_id, message.text, exclude_id=subject_id):
            await state.clear()
            await message.answer("❌ Такой предмет уже есть.")
            return
        ok = update_subject_name(user_id, subject_id, message.text)
    else:
        note = "" if message.text.strip() == "-" else message.text
        ok = update_subject_note(user_id, subject_id, note)

    await state.clear()
    await message.answer("✅ Предмет обновлён" if ok else "❌ Предмет не найден")
