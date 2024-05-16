import datetime
from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

import asyncio

from app.database.dao.user import get_user_by_user_id, delete_user, add_user, get_full_user_info
from app.database.dao.filter import add_filter
from app.database.dao.uni import add_uni, get_uni_by_id
from app.database.dao.sub import get_subscription_by_user_id, add_subscription, delete_subscription

from app.keyboards.reply import get_keyboard, get_menu_keyboard
from app.handlers.fill import start_auth

from app.common.text import premium_text

from app.common.uni_list import uni_data
# from tests.test_data import data_user, data_filter


premium_router = Router()


premium_kb = get_keyboard(
    "💎МЕСЯЦ",
    "💎ГОД",
    "1 минута",
    "Отменить подписку",
    "Назад",
    sizes=(2, 1, 1, 1, )
)
    
    
@premium_router.message(F.text == "💎Premium")
async def premium(message: Message, session: AsyncSession):
    await message.answer(premium_text, reply_markup=premium_kb)
        
        
@premium_router.message(F.text == "1 минута")
async def minute(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
    else:
        
        current_date = datetime.datetime.now()
        finish_date = current_date + datetime.timedelta(minutes=1)
        
        data = {
            "user_id": message.from_user.id,
            "finish_date": finish_date.date(),
            "subscription_type": "month"
        }

        await add_subscription(session, data)
        await message.answer("Вы успешно оформили подписку на месяц!", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))

        
@premium_router.message(F.text == "💎МЕСЯЦ")
async def month(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
    else:
        
        current_date = datetime.datetime.now()
        finish_date = current_date + datetime.timedelta(days=30)
        
        data = {
            "user_id": message.from_user.id,
            "finish_date": finish_date,
            "subscription_type": "month"
        }

        await add_subscription(session, data)
        await message.answer("Вы успешно оформили подписку на месяц!", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))
        
        
@premium_router.message(F.text == "💎ГОД")
async def month(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
    else:
        
        current_date = datetime.datetime.now()
        finish_date = current_date + datetime.timedelta(days=365)
        
        data = {
            "user_id": message.from_user.id,
            "finish_date": finish_date,
            "subscription_type": "month"
        }

        await add_subscription(session, data)
        await message.answer("Вы успешно оформили подписку на год!", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))


@premium_router.message(F.text == "Отменить подписку")
async def refuse_subscription(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await delete_subscription(session, message.from_user.id)
        await message.answer("Вы отменили подписку!")
    else:
        await message.answer("Вы еще не оформили подписку!")