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

from app.keyboards.reply import get_keyboard, get_menu_keyboard
from app.handlers.fill import start_auth

from app.common.uni_list import uni_data
# from tests.test_data import data_user, data_filter


base_router = Router()

profile_kb = get_keyboard(
    "🔄",
    "📝",
    "🖼",
    "Выложить проект",
    "Мои проекты",
    "Назад",
    placeholder="Выберите действие",
    sizes=(3, 2, 1)
)


register_kb = get_keyboard(
    "Заполнить анкету",
    "Назад",
    placeholder="Выберите действие",
    sizes=(2,)
)


class Start(StatesGroup):
    is_auth = State()


@base_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    # await delete_user(session, message.from_user.id)
    await state.set_state(Start.is_auth)
    await message.answer_sticker("CAACAgIAAxkBAAISCmY5JbkIzcX3LSJnp4z5ULUt7PA3AAKLAQACK15TC6NhvGkkNINQNQQ")
    await message.answer(f"Хочешь найти друзей или вторую половинку со своего университета?💫\n\n", 
                         reply_markup=get_keyboard("Разумеется🔥", "Хотелось бы⭐️"))
    
    for uni in uni_data:
        await add_uni(session, uni)
    # for test_person in data_user:
    #     await add_user(session, test_person)
    # for test_filter in data_filter:
    #     await add_filter(session, test_filter)
        
        
        
@base_router.message(StateFilter(Start.is_auth))
async def start_is_auth(message: Message, state: FSMContext, session: AsyncSession):
    user = await get_user_by_user_id(session, message.from_user.id)
    if user:
        await state.clear()
        await message.answer("Главное меню", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))
    else:
        await state.clear()
        await start_auth(message, state)
    
    
    
@base_router.message(F.text == "🙍🏻‍♂️Мой профиль")
async def my_profile(message: Message, session: AsyncSession):
    user = await get_full_user_info(session, message.from_user.id)
    if user:
        await message.answer_photo(user.photo, caption=f'🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n🏛<b>{user["uni_name"]}</b>\n🔍<b>{user["target"]}</b>\n\n{user["description"]}\n\n🔄 - Заполнить анкету заново\n📝 - Изменить описание\n🖼 - Изменить фото', reply_markup=profile_kb)
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
        
@base_router.message(F.text == "Назад")
async def back(message: Message):
    await message.answer("Меню", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))
    

@base_router.message(F.text)
async def not_handled(message: Message):
    await message.answer("Я не понимаю эту команду")


@base_router.message(F.photo)
async def not_handled(message: Message):
    await message.answer(message.photo[-1].file_id)


