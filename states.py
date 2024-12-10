from aiogram.fsm.state import State, StatesGroup
class User(StatesGroup):
    lang = State()

class AsCaching(StatesGroup):
    last_message_id = State()
    chat_id = State()