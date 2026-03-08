from aiogram.fsm.state import State, StatesGroup


class AskState(StatesGroup):
    waiting_for_question = State()


class ReplyState(StatesGroup):
    waiting_for_answer = State()


class BroadcastState(StatesGroup):
    waiting_for_message = State()
