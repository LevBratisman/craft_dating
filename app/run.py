import asyncio
from contextlib import asynccontextmanager
import logging
from aiogram import Dispatcher, Bot
from aiogram.types import Update
from fastapi import FastAPI, Request, Response
import uvicorn

from config import settings

from handlers.base import base_router
from handlers.fill import fill_router
from handlers.search import search_router
from handlers.profile import profile_router
from handlers.search_settings import search_settings_router
from handlers.commands import cmd_router
from handlers.like import like_router
from handlers.admin.admin import admin_router

from common.cmd_list import private


from database.init import create_db, drop_db

from common.cities import load_cities
from middlewares.db import DataBaseSession
from database.init import async_session_maker

#########################################################
#----------------------run.py---------------------------#

@asynccontextmanager
async def lifespan(app):
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    await bot.set_my_commands(private)
    dp.update.middleware(DataBaseSession(session_pool=async_session_maker))
    # Start the bot
    await bot.delete_webhook(drop_pending_updates=True)
    yield
    

app = FastAPI(lifespan=lifespan)
    

@app.api_route("/", methods=["GET", "POST"])
async def webhook(update: dict):
    telegram_update = Update(**update)
    await dp.feed_update(bot=bot, update=telegram_update)

# Initialize Bot and Dispatcher
bot = Bot(token=settings.BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()


# Include Routers
dp.include_router(cmd_router)
dp.include_router(fill_router)
dp.include_router(admin_router)
dp.include_router(profile_router)
dp.include_router(search_settings_router)
dp.include_router(search_router)
dp.include_router(like_router)
dp.include_router(base_router)




# startup and shutdown handlers
async def on_startup(bot):
    logging.info("Starting bot")
    
    is_dropped = False
    if is_dropped:
        await drop_db()
        
    await create_db()


async def on_shutdown(bot):
    logging.info("Shutting down bot")
    

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        uvicorn.run(app, host="127.0.0.1", port=5000)
        # asyncio.run(main())
    except KeyboardInterrupt:
        print("error")
        #https://api.telegram.org/bot6727500986:AAE5xqYxeyOwV7jNPOJDPzT1_l4Dd4bOjY4/setWebhook?url=https://630b-2a00-1fa0-4a3-a6ff-55d1-c84-6212-3e50.ngrok-free.app
        #https://api.telegram.org/bot6727500986:AAE5xqYxeyOwV7jNPOJDPzT1_l4Dd4bOjY4/getWebhookInfo