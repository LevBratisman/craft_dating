from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import Bot, Router, F
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.database.dao.filter import add_filter
from app.database.dao.like import add_like_stats
from app.database.dao.uni import get_uni_by_id, get_uni_by_name
from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard, get_menu_keyboard
from app.database.dao.user import add_user
from app.filters.admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession


admin_kb = get_keyboard(
    "🔉Сделать рассылку",
    "📊Статистика",
    "Добавить бота",
    "⬅️Назад к меню",
    sizes=(2, 1, 1, )
)

adbot_router = Router()
adbot_router.message.filter(IsAdmin())

pop_uni_kb = get_callback_btns(
    btns={
        "Московский политех": "Московский политех",
        "Здесь нет моего ВУЗа": "none"
    },
    sizes=(1, )
)


class AuthBotInfo(StatesGroup):
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
    
    
@adbot_router.message(StateFilter(None), F.text == "Добавить бота")
async def start_auth(message: Message, state: FSMContext):
    await state.set_state(AuthBotInfo.user_id)
    await message.answer_sticker("CAACAgIAAxkBAAISCGY15K9Srgqdh2Ksms_n38c69thAAAKPAQACK15TC1JZlsxRJSLCNAQ", reply_markup=ReplyKeyboardRemove())
    await message.answer("Введите user id")
    
    
    
@adbot_router.message(StateFilter(AuthBotInfo.user_id), F.text)
async def get_user_id(message: Message, state: FSMContext):
    await state.update_data(user_id=int(message.text))
    await state.set_state(AuthBotInfo.uni)
    await message.answer("С какого вы университета?", reply_markup=pop_uni_kb)
    
@adbot_router.callback_query(StateFilter(AuthBotInfo.uni), F.data)
async def get_uni(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == "none":
        await callback.message.edit_text(f"К сожалению, сервис пока поддерживает только эти университеты\nВыберите один из списка", reply_markup=pop_uni_kb)
        return
    else:
        uni = await get_uni_by_name(session, callback.data)
        print(uni, uni.name)  
        await state.update_data(uni=uni.id)
        await state.set_state(AuthBotInfo.target)
        await callback.message.edit_text("Что вы ищите?", reply_markup=get_callback_btns(
            btns={"Дружбу": "Дружба", "Отношения": "Отношения", "Как пойдет": "Как пойдет"},
            sizes=(2, 1)
        ))
        
    
    
@adbot_router.callback_query(StateFilter(AuthBotInfo.target), F.data)
async def get_craft(callback: CallbackQuery, state: FSMContext):
    await state.update_data(target=callback.data)
    await state.set_state(AuthBotInfo.sex)
    await callback.message.edit_text("Ваш пол:", reply_markup=get_callback_btns(
        btns={"Парень": "Парень", "Девушка": "Девушка"},
        sizes=(2,)
    ))
    
    
@adbot_router.callback_query(StateFilter(AuthBotInfo.sex), F.data)
async def get_craft(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sex=callback.data)
    await state.set_state(AuthBotInfo.sex_target)
    await callback.message.edit_text("Кого вы ищите?", reply_markup=get_callback_btns(
        btns={"Девушку": "Девушка", "Парня": "Парень", "Все равно": "Все равно"},
        sizes=(2,)
    ))
    
    
@adbot_router.callback_query(StateFilter(AuthBotInfo.sex_target), F.data)
async def get_target(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sex_target=callback.data)
    await state.set_state(AuthBotInfo.name)
    await callback.message.edit_text("Как вас зовут?")
        

@adbot_router.message(StateFilter(AuthBotInfo.name), F.text)
async def get_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(AuthBotInfo.age)
    await message.answer("Сколько вам лет?")
    
    
@adbot_router.message(StateFilter(AuthBotInfo.age), F.text)
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
    await state.set_state(AuthBotInfo.photo)
    await message.answer("Мы на финишной прямой! Прикрепите свою фотографию")
    
    
    
@adbot_router.message(StateFilter(AuthBotInfo.photo), F.photo)
async def get_photo(message: Message, state: FSMContext):
    await state.update_data(photo=message.photo[-1].file_id)
    await state.set_state(AuthBotInfo.description)
    await message.answer("Расскажите о себе", reply_markup=get_keyboard("Пропустить"))
    
    
@adbot_router.message(StateFilter(AuthBotInfo.description), F.text)
async def get_description(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "Пропустить":
        await state.update_data(description=' ')
    else:
        await state.update_data(description=message.text)
        
    
        
    await state.update_data(username="bot")
    
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
        "target": data["target"],
        "description": data["description"],
        "iterator": 0,
        "like_iterator": 0,
        "project_iterator": 0
    }
    
    data_filter = {
        "user_id": data["user_id"],
        "target": None,
        "sex_target": data["sex_target"],
        "uni_id": data["uni"],
    }
    

    await add_user(session, data_user)
    await add_filter(session, data_filter)
    
    uni = await get_uni_by_id(session, data["uni"])
    
    await message.answer("Бот успешно добавлен", reply_markup=admin_kb)
    await message.answer_photo(data["photo"], caption=f'🎴{data["name"]}, {data["age"]}\n🏛<b>{uni.name}</b>\n🔍<b>{data["target"]}</b>\n\n{data["description"]}')
    await state.clear()