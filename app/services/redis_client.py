import redis.asyncio as redis


from app.configs import REDIS_URL
from .translations import get_use_lang

async def get_redis():
    redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return redis_client

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