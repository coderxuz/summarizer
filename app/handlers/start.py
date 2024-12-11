from aiogram import Router
from aiogram.types import Message
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext


from app.services.redis_client import get_redis , get_use_lang, get_user_language_redis, set_user_language_redis
from app.services.translations import get_translations
from app.configs import logger
from app.keyboards.inline import start_inline_keyboard

router = Router()

@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    redis_client = await get_redis()
    user_data = await state.get_data()

    lang_code = await get_user_language_redis(
        redis_client,
        message.from_user.id,
        query_or_message=message,
        user_data=user_data,
    )
    logger.info(lang_code)
    await set_user_language_redis(redis_client, message.from_user.id, lang_code)
    await state.update_data(lang=lang_code)

    logger.debug(lang_code)

    help_txt = get_translations(lang_code, "help_txt")
    choose_lang = get_translations(lang_code, "choose_lang")
    send_yt_vd = get_translations(lang_code, "send_video")

    keyboard = await start_inline_keyboard(
        lang=choose_lang, send_url=send_yt_vd, help_txt=help_txt
    )

    message_inline = await message.answer(
        get_translations(lang=lang_code, key="start"), reply_markup=keyboard
    )

    await state.update_data(last_message_id=message_inline.message_id)
    await state.update_data(chat_id=message.chat.id)