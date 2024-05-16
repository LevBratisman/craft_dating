from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao.user import get_user_by_user_id, update_user_description, update_user_photo, get_full_user_info
from app.database.dao.uni import get_uni_by_id

from app.keyboards.reply import get_keyboard
from app.keyboards.inline import get_callback_btns
from app.handlers.search import start_search
from app.handlers.fill import start_auth
from app.handlers.base import profile_kb, my_profile

from tests.test_data import data


profile_router = Router()


confirmation_kb = get_callback_btns(
    btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
    sizes=(2,)
)


class Description(StatesGroup):
    user_id = State()
    description = State()
    confirmation = State()


class Photo(StatesGroup):
    user_id = State()
    photo = State()
    confirmation = State()


@profile_router.message(F.text == "🔄")
async def start_search(message: Message, state: FSMContext):
    await start_auth(message, state)
    
    
# -------------------------------- DESCRIPTION FSM -----------------------------
    
@profile_router.message(F.text == "📝")
async def desc_change(message: Message, state: FSMContext):
    await state.set_state(Description.description)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Расскажите о себе", reply_markup=get_keyboard("Сбросить"))
    
    
@profile_router.message(StateFilter(Description.description), F.text)
async def get_description(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "Сбросить":
        await state.update_data(description='')
    else:
        await state.update_data(description=message.text)
        
    data = await state.get_data()
    user = await get_full_user_info(session, message.from_user.id)
    await state.set_state(Description.confirmation)
    
    await message.answer("Ваша анкета:", reply_markup=ReplyKeyboardRemove())
        
    await message.answer_photo(user.photo, caption=f'🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n<b>🏛{user["uni_name"]}</b>\n🔍<b>{user["target_desc"]}</b>\n\n{data["description"]}', reply_markup=confirmation_kb)
    
    
@profile_router.message(StateFilter(Description.description))
async def wrong_description(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Неверный формат! Введите текст")
        
    
@profile_router.callback_query(StateFilter(Description.confirmation), F.data)
async def desc_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    
    data = await state.get_data()
    
    if callback.data == "Подтвердить":
        await update_user_description(session, data["user_id"], data["description"])
        
    user = await get_full_user_info(session, data["user_id"])
    await state.clear()
    await callback.message.delete()
    await callback.message.answer_photo(photo=user.photo, caption=f'🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n<b>🏛{user["uni_name"]}</b>\n🔍<b>{user["target_desc"]}</b>\n\n{user["description"]}\n\n🔄 - Заполнить анкету заново\n📝 - Изменить описание\n🖼 - Изменить фото', reply_markup=profile_kb)
    
    
# -------------------------------- PHOTO FSM -----------------------------
    
    
@profile_router.message(F.text == "🖼")
async def photo_change(message: Message, state: FSMContext):
    await state.set_state(Photo.photo)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Приложите фото", reply_markup=ReplyKeyboardRemove())
    
    
@profile_router.message(StateFilter(Photo.photo), F.photo)
async def get_photo(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(photo=message.photo[-1].file_id)
        
    await state.set_state(Photo.confirmation)
    
    await message.answer("Подтвердить изменения?", reply_markup=confirmation_kb)
    
    
@profile_router.message(StateFilter(Photo.photo))
async def wrong_photo(message: Message, state: FSMContext):
    await message.answer("Неверный формат! Приложите фото")
        
    
@profile_router.callback_query(StateFilter(Photo.confirmation), F.data)
async def photo_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    
    if callback.data == "Подтвердить":
        await update_user_photo(session, data["user_id"], data["photo"])
        
    user = await get_full_user_info(session, data["user_id"])
    await state.clear()
    await callback.message.delete()
    await callback.message.answer_photo(photo=user.photo, caption=f'🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n<b>🏛{user["uni_name"]}</b>\n🔍<b>{user["target_desc"]}</b>\n\n{user["description"]}\n\n🔄 - Заполнить анкету заново\n📝 - Изменить описание\n🖼 - Изменить фото', reply_markup=profile_kb)


# -------------------------------------------------------------


