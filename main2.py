import asyncio
from os import getenv
import re
import sys


from configs import logger
from services import (
    get_translations,
    get_use_lang,
    get_redis,
    get_user_language_redis,
    set_user_language_redis,
)
from keyboards import choose_lang_keyb, start_inline_keyboard, lang_keyboards, main_manu

from watchgod import awatch
from aiogram import Bot, Dispatcher
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardRemove,
    ContentType,
)
import aiogram.types as types
from aiogram.filters import CommandStart, Command
from dotenv import load_dotenv

load_dotenv()

TOKEN = getenv("TOKEN")
bot = Bot(token=TOKEN)


dp = Dispatcher()


@dp.message(CommandStart())
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


@dp.callback_query(lambda c: c.data == "lang")
async def change_lang(callback_query: types.CallbackQuery, state: FSMContext):
    keyboard = await lang_keyboards()
    user_data = await state.get_data()
    redis_client = await get_redis()

    lang_code = await get_user_language_redis(
        redis_client=redis_client,
        user_id=callback_query.from_user.id,
        query_or_message=callback_query,
        user_data=user_data,
    )
    logger.info(user_data)
    await callback_query.message.answer(
        get_translations(lang_code, "choose_lang"), reply_markup=keyboard
    )
    await bot.delete_message(
        chat_id=user_data.get("chat_id"), message_id=user_data.get("last_message_id")
    )


@dp.callback_query(lambda c: c.data == "send_url")
async def send_url(callback_query: types.CallbackQuery, state: FSMContext):
    user_data = await state.get_data()

    redis_client = await get_redis()

    lang_code = await get_user_language_redis(
        redis_client=redis_client,
        user_id=callback_query.from_user.id,
        query_or_message=callback_query,
        user_data=user_data,
    )
    await callback_query.message.answer(get_translations(lang_code, "send_link"), parse_mode='Markdown')
    await bot.delete_message(
        chat_id=user_data.get("chat_id"), message_id=user_data.get("last_message_id")
    )


@dp.message(lambda msg: msg.text in ["English", "O'zbek", "Русский"])
async def set_language(message: Message, state: FSMContext):
    redis_client = await get_redis()

    match message.text:
        case "English":
            lang = "en"
        case "O'zbek":
            lang = "uz"
        case "Русский":
            lang = "ru"
    await set_user_language_redis(redis_client, message.from_user.id, lang_code=lang)
    await message.answer(
        get_translations(lang, "lang_changed"),
        reply_markup=await main_manu(lang_code=lang),
    )


@dp.message(
    lambda msg: msg.text in ["Choose language", "Tilni tanlang", "Выберите язык"]
)
async def handle_lang_message(message: types.Message, state: FSMContext):
    keyboard = await lang_keyboards()
    user_data = await state.get_data()

    logger.info(user_data)
    await message.answer(get_translations("ru", "choose_lang"), reply_markup=keyboard)


async def main():
    logger.info("bot running")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
