from aiogram import Router
import aiogram.types as types
from aiogram.fsm.context import FSMContext

from app.configs import logger
from app.services.redis_client import get_redis,get_user_language_redis
from app.services.translations import get_translations

router = Router()

@router.message(lambda msg:msg.text in ['Help','Yordam','Помощь'])
async def help_command(message:types.Message, state:FSMContext):
    redis_client = await get_redis()
    user_data = await state.get_data()

    lang_code = await get_user_language_redis(
        redis_client,
        message.from_user.id,
        query_or_message=message,
        user_data=user_data,
    )
    await message.answer(get_translations(lang=lang_code, key='help_command'),parse_mode='HTML')