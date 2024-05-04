from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_user_by_user_id, delete_user, add_user

from app.keyboards.reply import get_keyboard
from app.handlers.search import start_search
from app.handlers.fiil import start_auth
from app.handlers.base import start_kb

from tests.test_data import data


profile_router = Router()



@profile_router.message(F.text == "1")
async def start_search(message: Message, state: FSMContext):
    await start_auth(message, state)
    


@profile_router.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Меню", reply_markup=start_kb)

