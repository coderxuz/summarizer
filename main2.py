import asyncio

from app.configs import logger
from app import dp, bot
from app.handlers import start, lang, sending_url,help



async def main():
    logger.info("bot running")
    dp.include_router(start.router)
    dp.include_router(lang.router)
    dp.include_router(help.router)
    dp.include_router(sending_url.router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
