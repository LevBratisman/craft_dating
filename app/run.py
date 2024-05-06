import asyncio
import logging
from aiogram import Dispatcher, Bot


from config import settings

from handlers.base import base_router
from handlers.fill import fill_router
from handlers.search import search_router
from handlers.profile import profile_router
from handlers.search_settings import search_settings_router


from database.init import create_db, drop_db

from common.cities import load_cities
from middlewares.db import DataBaseSession
from database.init import async_session_maker

#########################################################
#----------------------run.py---------------------------#


# Initialize Bot and Dispatcher
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


# Include Routers
dp.include_router(fill_router)
dp.include_router(profile_router)
dp.include_router(search_settings_router)
dp.include_router(search_router)
dp.include_router(base_router)




# startup and shutdown handlers
async def on_startup(bot):
    load_cities()
    logging.info("Starting bot")
    
    is_dropped = False
    if is_dropped:
        await drop_db()
        
    await create_db()


async def on_shutdown(bot):
    logging.info("Shutting down bot")


# main function
async def main():
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    # await bot.set_my_commands(private)
    dp.update.middleware(DataBaseSession(session_pool=async_session_maker))
    # Start the bot
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("error")