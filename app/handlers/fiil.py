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

from app.database.dao import add_user, add_filter, add_like_stats

from app.handlers.base import start_kb


fill_router = Router()


class AuthInfo(StatesGroup):
    user_id = State()
    username = State()
    target = State()
    sex = State()
    sex_target = State()
    name = State()
    age = State()
    age_from = State()
    age_to = State()
    city = State()
    photo = State()
    description = State()
    
    
@fill_router.message(StateFilter(None), F.text == "Заполнить анкету")
async def start_auth(message: Message, state: FSMContext):
    await state.set_state(AuthInfo.target)
    await message.answer("Поехали!", reply_markup=ReplyKeyboardRemove())
    await message.answer("Что вы ищите?", reply_markup=get_callback_btns(
        btns={"Дружба": "Дружба", "Отношения": "Отношения"},
        sizes=(2,)
    ))
    
    
@fill_router.callback_query(StateFilter(AuthInfo.target), F.data)
async def get_craft(callback: CallbackQuery, state: FSMContext):
    await state.update_data(target=callback.data)
    await state.set_state(AuthInfo.sex)
    await callback.message.edit_text("Ваш пол:", reply_markup=get_callback_btns(
        btns={"Парень": "Парень", "Девушка": "Девушка"},
        sizes=(2,)
    ))
    
    
@fill_router.callback_query(StateFilter(AuthInfo.sex), F.data)
async def get_craft(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sex=callback.data)
    await state.set_state(AuthInfo.sex_target)
    await callback.message.edit_text("Кого вы ищите?", reply_markup=get_callback_btns(
        btns={"Девушку": "Девушка", "Парня": "Парень", "Все равно": "Все равно"},
        sizes=(2,)
    ))
    
    
@fill_router.callback_query(StateFilter(AuthInfo.sex_target), F.data)
async def get_target(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sex_target=callback.data)
    await state.set_state(AuthInfo.name)
    await callback.message.edit_text("Как вас зовут?")
        

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
    elif int(message.text) < 14:
        await message.answer("Возраст должен быть больше 13, повторите ввод")
        return 
    elif int(message.text) > 80:
        await message.answer("Люди столько не живут ;) Возраст должен быть меньше 80 повторите ввод")
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
    await message.answer("Мы почти у финиша! Приложите фото")
    
    
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
    await state.update_data(username=message.from_user.username)
    
    data = await state.get_data()
    
    if data["age"] > 18 and data["age"] < 76: 
        await state.update_data(age_from=data["age"] - 5)
        await state.update_data(age_to=data["age"] + 5)
    elif data["age"] <= 18:
        await state.update_data(age_from=14)
        await state.update_data(age_to=data["age"] + 5)
    elif data["age"] >= 76:
        await state.update_data(age_from=data["age"] - 5)
        await state.update_data(age_to=80)
        
    data = await state.get_data()
        
    data_user = {
        "user_id": data["user_id"],
        "username": data["username"],
        "sex": data["sex"],
        "name": data["name"],
        "age": data["age"],
        "city": data["city"],
        "photo": data["photo"],
        "description": data["description"],
        "iterator": 0,
        "like_iterator": 0
    }
    
    data_filter = {
        "user_id": data["user_id"],
        "target": data["target"],
        "sex_target": data["sex_target"],
        "age_from": data["age_from"],
        "age_to": data["age_to"],
        "city": "None",
    }
    
    like_filter = {
        "user_id": data["user_id"],
        "liked_users_id": ""
    }
    

    await add_user(session, data_user)
    await add_filter(session, data_filter)
    await add_like_stats(session, like_filter)
    
    await message.answer("Ваша анкета успешно заполнена", reply_markup=start_kb)
    await message.answer_photo(data["photo"], caption=f'{data["name"]}, {data["age"]}\nГород: {data["city"]}\n\n{data["description"]}')
    await state.clear()