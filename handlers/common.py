from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from keyboards.main_menu import main_menu
from services.subject_service import get_subjects
from services.tasks_service import get_tasks_due_in

router = Router()

UPCOMING_DAYS = 7


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
        "/upcoming — ближайшие дедлайны\n"
        "/subjects — управление предметами\n"
        "/done — отметить задание выполненным\n"
        "/delete — удалить задание\n"
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



@router.message(Command("upcoming"))
@router.message(F.text == "📅 Ближайшие дедлайны")
async def upcoming_deadlines(message: Message):
    user_id = message.from_user.id
    tasks = get_tasks_due_in(user_id=user_id, days=UPCOMING_DAYS)

    if not tasks:
        await message.answer(f"📅 На ближайшие {UPCOMING_DAYS} дней дедлайнов нет.")
        return

    subjects = {s["id"]: s["name"] for s in get_subjects(user_id=user_id)}
    lines = []
    for t in tasks:
        subject_name = subjects.get(t["subject_id"], "—")
        line = f"📌 {t['title']}\n📚 {subject_name}\n📅 Дедлайн: {t['deadline']}"
        if t["note"]:
            line += f"\n📝 {t['note']}"
        lines.append(line)

    await message.answer(
        f"📅 Ближайшие дедлайны ({UPCOMING_DAYS} дней):\n\n" + "\n\n".join(lines)
    )


@router.message(F.text == "❓ Помощь")
async def help_button_handler(message: Message):
    await help_handler(message)
