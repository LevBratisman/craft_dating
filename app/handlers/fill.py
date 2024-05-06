from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard
from app.common.cities import CITIES_SET

from app.database.dao.user import add_user
from app.database.dao.filter import add_filter
from app.database.dao.like import add_like_stats
from app.database.dao.uni import get_uni_by_name, get_uni_by_id

from app.handlers.base import start_kb


fill_router = Router()


pop_uni_kb = get_callback_btns(
    btns={
        "Московский политех": "Московский политех",
        "МГУ": "МГУ",
        "РУДН": "РУДН",
        "МФТИ": "МФТИ",
        "Здесь нет моего ВУЗа": "none"
    },
    sizes=(2, 2, 1)
)


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
    uni = State()
    photo = State()
    description = State()
    
    
@fill_router.message(StateFilter(None), F.text == "Заполнить анкету")
async def start_auth(message: Message, state: FSMContext):
    await state.set_state(AuthInfo.uni)
    await message.answer_sticker("CAACAgIAAxkBAAISCGY15K9Srgqdh2Ksms_n38c69thAAAKPAQACK15TC1JZlsxRJSLCNAQ", reply_markup=ReplyKeyboardRemove())
    await message.answer("С какого вы университета?", reply_markup=pop_uni_kb)
    
    
    
@fill_router.callback_query(StateFilter(AuthInfo.uni), F.data)
async def get_uni(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == "none":
        await callback.message.edit_text(f"К сожалению, сервис пока поддерживает только эти университеты\nВыберите один из списка", reply_markup=pop_uni_kb)
        return
    else:
        uni = await get_uni_by_name(session, callback.data)
        print(uni, uni.name)  
        await state.update_data(uni=uni.id)
        await state.set_state(AuthInfo.target)
        await callback.message.edit_text("Что вы ищите?", reply_markup=get_callback_btns(
            btns={"Дружбу": "Дружба", "Отношения": "Отношения"},
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
    await state.set_state(AuthInfo.photo)
    await message.answer("Мы на финишной прямой! Прикрепите свою фотографию")
    
    
    
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
    
    uni = await get_uni_by_id(session, data["uni"])
        
    data_user = {
        "user_id": data["user_id"],
        "username": data["username"],
        "sex": data["sex"],
        "name": data["name"],
        "age": data["age"],
        "city": uni.city,
        "uni_id": data["uni"],
        "photo": data["photo"],
        "description": data["description"],
        "iterator": 0,
        "like_iterator": 0
    }
    
    data_filter = {
        "user_id": data["user_id"],
        "target": data["target"],
        "sex_target": data["sex_target"],
        "uni_id": data["uni"],
    }
    
    like_filter = {
        "user_id": data["user_id"],
        "liked_users_id": ""
    }
    

    await add_user(session, data_user)
    await add_filter(session, data_filter)
    await add_like_stats(session, like_filter)
    
    uni = await get_uni_by_id(session, data["uni"])
    
    await message.answer("Ваша анкета успешно заполнена", reply_markup=start_kb)
    await message.answer_photo(data["photo"], caption=f'🎴{data["name"]}, {data["age"]}\n🏛<b>{uni.name}</b>\n\n{data["description"]}')
    await state.clear()