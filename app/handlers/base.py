from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_user_by_user_id, del_user_by_user_id

from app.keyboards.reply import get_keyboard


base_router = Router()


start_kb = get_keyboard(
    "Мой профиль",
    "Искать людей",
    placeholder="Выберите действие",
    sizes=(2,)
)

register_kb = get_keyboard(
    "Заполнить анкету",
    "Назад",
    placeholder="Выберите действие",
    sizes=(2,)
)


@base_router.message(CommandStart())
async def start(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await del_user_by_user_id(session, message.from_user.id)
    await message.answer("Wellcome", reply_markup=start_kb)
    
    
@base_router.message(F.text == "Мой профиль")
async def my_profile(message: Message, session: AsyncSession):
    user = await get_user_by_user_id(session, message.from_user.id)
    print(user)
    if user:
        await message.answer_photo(user.photo, caption=f'{user.name}, {user.age}\nГород: {user.city}\nСфера: {user.craft}\n\n{user.description}')
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
        
@base_router.message(F.text == "Назад")
async def back(message: Message):
    await message.answer("Меню", reply_markup=start_kb)
    

@base_router.message(F.text)
async def not_handled(message: Message):
    await message.answer("I don't know this command")




