from aiogram import Router
from aiogram.types import Message
import aiogram.types as types
from aiogram.fsm.context import FSMContext

from app import bot
from app.keyboards.reply import lang_keyboards, main_manu
from app.services.redis_client import get_redis, get_user_language_redis, set_user_language_redis
from app.services.translations import get_translations
from app.configs import logger

router = Router()

@router.callback_query(lambda c: c.data == "lang")
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

@router.message(lambda msg: msg.text in ["English", "O'zbek", "Русский"])
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

@router.message(
    lambda msg: msg.text in ["Choose language", "Tilni tanlang", "Выберите язык"]
)
async def handle_lang_message(message: types.Message, state: FSMContext):
    keyboard = await lang_keyboards()
    user_data = await state.get_data()

    logger.info(user_data)
    await message.answer(get_translations("ru", "choose_lang"), reply_markup=keyboard)