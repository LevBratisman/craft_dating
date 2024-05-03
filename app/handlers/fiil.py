from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard
from app.common.cities import CITIES_SET
from app.common.craft_list import CRAFTS_SET

from app.database.dao import add_user

from app.handlers.base import start_kb


fill_router = Router()

class AuthInfo(StatesGroup):
    user_id = State()
    craft = State()
    name = State()
    age = State()
    city = State()
    photo = State()
    description = State()
    
    
@fill_router.message(StateFilter(None), F.text == "Заполнить анкету")
async def start_auth(message: Message, state: FSMContext):
    await state.set_state(AuthInfo.craft)
    await message.answer("Поехали!", reply_markup=ReplyKeyboardRemove())
    await message.answer("В какой сфере вы развиваетесь?", reply_markup=get_callback_btns(
        btns={value: value for value in CRAFTS_SET},
        sizes=(2,)
    ))
    
    
@fill_router.callback_query(StateFilter(AuthInfo.craft), F.data)
async def get_craft(callback: CallbackQuery, state: FSMContext):
    await state.update_data(craft=callback.data)
    await state.set_state(AuthInfo.name)
    await callback.message.delete()
    await callback.message.answer("Как вас зовут?")
    

@fill_router.message(StateFilter(AuthInfo.name), F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AuthInfo.age)
    await message.answer("Сколько вам лет?")
    
    
@fill_router.message(StateFilter(AuthInfo.age), F.text)
async def get_age(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Возраст должен быть числом, повторите ввод")
        return
    await state.update_data(age=int(message.text))
    await state.set_state(AuthInfo.city)
    await message.answer("В каком городе вы живете?")
    
    
@fill_router.message(StateFilter(AuthInfo.city), F.text)
async def get_city(message: Message, state: FSMContext):
    if message.text.lower() not in CITIES_SET:
        await message.answer("Такого города нет, повторите ввод")
        return
    await state.update_data(city=message.text.capitalize())
    await state.set_state(AuthInfo.photo)
    await message.answer("Приложите фото")
    
    
@fill_router.message(StateFilter(AuthInfo.photo), F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AuthInfo.description)
    await message.answer("Расскажите о себе", reply_markup=get_keyboard("Пропустить"))
    
    
@fill_router.message(StateFilter(AuthInfo.description), F.text)
async def get_description(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "Пропустить":
        await state.update_data(description=' ')
    else:
        await state.update_data(description=message.text)
    await state.update_data(user_id=message.from_user.id)
    data = await state.get_data()
    await add_user(session, data)
    await message.answer("Ваша анкета успешно заполнена", reply_markup=start_kb)
    await message.answer_photo(data["photo"], caption=f'{data["name"]}, {data["age"]}\nГород: {data["city"]}\nСфера: {data["craft"]}\n\n{data["description"]}')
    await state.clear()