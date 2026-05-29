from aiogram.fsm.state import State, StatesGroup


class AddSubjectStates(StatesGroup):
    waiting_name = State()
    waiting_note = State()


class EditSubjectStates(StatesGroup):
    waiting_value = State()


class AddTaskStates(StatesGroup):
    waiting_subject = State()
    waiting_title = State()
    waiting_deadline = State()
    confirm_past_deadline = State()
    waiting_note = State()


class EditTaskStates(StatesGroup):
    waiting_value = State()
    confirm_past_deadline = State()
