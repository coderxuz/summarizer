from aiogram.fsm.state import State, StatesGroup
class AsCaching(StatesGroup):
    last_message_id = State()
    chat_id = State()
    last_video_id = State()