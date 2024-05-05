from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_user_by_user_id, delete_user, add_user, add_filter

from app.keyboards.reply import get_keyboard

from tests.test_data import data_user, data_filter


base_router = Router()

profile_kb = get_keyboard(
    "🔄",
    "📝",
    "🖼",
    "Назад",
    placeholder="Выберите действие",
    sizes=(3, 1)
)


start_kb = get_keyboard(
    "Искать людей",
    "Мой профиль",
    "Параметры поиска",
    placeholder="Выберите действие",
    sizes=(1, 2)
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
    await delete_user(session, message.from_user.id)
    await message.answer("Wellcome", reply_markup=start_kb)
    for test_person in data_user:
        await add_user(session, test_person)
    for test_filter in data_filter:
        await add_filter(session, test_filter)
    
    
@base_router.message(F.text == "Мой профиль")
async def my_profile(message: Message, session: AsyncSession):
    user = await get_user_by_user_id(session, message.from_user.id)
    if user:
        await message.answer_photo(user.photo, caption=f'{user.name}, {user.age}\nГород: {user.city}\n{user.description}\n\n🔄 - Заполнить анкету заново\n📝 - Изменить описание\n🖼 - Изменить фото', reply_markup=profile_kb)
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
        
@base_router.message(F.text == "Назад")
async def back(message: Message):
    await message.answer("Меню", reply_markup=start_kb)
    

@base_router.message(F.text)
async def not_handled(message: Message):
    await message.answer("I don't know this command")


@base_router.message(F.photo)
async def not_handled(message: Message):
    await message.answer(message.photo[-1].file_id)


