import json
from aiogram.types import Message
from aiogram import types
from configs import logger
import redis.asyncio as redis
from dotenv import load_dotenv 
from os import getenv

load_dotenv()
REDIS_URL = getenv('REDIS_URL')

async def get_redis():
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

with open("translations.json", "r", encoding="utf-8") as file:
    translations = json.load(file)


def get_translations(lang, key):
    return translations.get(lang, {}).get(key, translations["ru"].get(key))

async def get_use_lang(query_or_message, user_data):
    # Check if the input is a CallbackQuery or a Message
    if isinstance(query_or_message, Message):
        lang_code = query_or_message.from_user.language_code
    elif isinstance(query_or_message, types.CallbackQuery):
        # Use `query_or_message.message.from_user.language_code` for CallbackQuery
        lang_code = query_or_message.message.from_user.language_code
    else:
        # Default to an empty string if the type is unexpected
        lang_code = None

    # Return user language preference or detected language
    return (
        user_data.get("lang") if user_data.get("lang") else lang_code
    )

async def set_user_language_redis(redis_client, user_id: int, lang_code: str):
    """Save the user's language preference in Redis asynchronously"""
    await redis_client.set(f"user:{user_id}:lang", lang_code)

# Function to get the user's language preference from Redis
async def get_user_language_redis(redis_client, user_id: int,query_or_message, user_data):
    """Retrieve the user's language preference from Redis asynchronously"""
    lang = await redis_client.get(f"user:{user_id}:lang")
    if not lang:
        lang = await get_use_lang(query_or_message, user_data)
    return lang or "en"  # Default to "en" if no language is set