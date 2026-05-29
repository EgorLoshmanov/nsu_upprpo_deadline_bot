from aiogram.fsm.state import State, StatesGroup


class AddSubjectStates(StatesGroup):
    waiting_name = State()
    waiting_note = State()


class AddTaskStates(StatesGroup):
    waiting_subject = State()
    waiting_title = State()
    waiting_deadline = State()
    waiting_note = State()
