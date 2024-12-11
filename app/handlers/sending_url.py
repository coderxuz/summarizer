from aiogram import Router
from aiogram.fsm.context import FSMContext
import aiogram.types as types

from app import bot
from app.services.redis_client import get_redis, get_user_language_redis
from app.services.translations import get_translations, translate_text
from app.services.summarizing import fetch_subtitles, get_video_id, summarize_text


router = Router()


@router.callback_query(lambda c: c.data == "send_url")
async def send_url(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    redis_client = await get_redis()

    lang_code = await get_user_language_redis(
        redis_client=redis_client,
        user_id=callback_query.from_user.id,
        query_or_message=callback_query,
        user_data=user_data,
    )
    await callback_query.message.answer(
        get_translations(lang_code, "send_link"), parse_mode="Markdown"
    )
    await bot.delete_message(
        chat_id=user_data.get("chat_id"), message_id=user_data.get("last_message_id")
    )


@router.message(
    lambda msg: msg.text and ("youtube.com" in msg.text or "youtu.be" in msg.text)
)
async def get_url(message: types.Message, state: FSMContext):
    redis_client = await get_redis()
    user_data = await state.get_data()

    video_id = await get_video_id(message.text)

    lang_code = await get_user_language_redis(
        redis_client,
        message.from_user.id,
        query_or_message=message,
        user_data=user_data,
    )
    fetching_msg = await message.answer(
        get_translations(lang=lang_code, key="fetching_subtitles")
    )

    subtitles = await fetch_subtitles(
        video_id=video_id, languages=["en",'ru','uz'], user_lang=lang_code
    )
    summarized = await summarize_text(subtitles, max_length=4000)
    
    trasnlated = await translate_text(summarized, target_language=lang_code)

    finished = await message.answer(trasnlated)

    if finished:
        await bot.delete_message(
            chat_id=message.chat.id,
            message_id=fetching_msg.message_id,
        )
