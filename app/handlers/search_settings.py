from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard
from app.common.cities import CITIES_SET

from app.database.dao import get_filter, update_target, update_city, update_sex_target, update_age

from app.handlers.base import start_kb


search_settings_router = Router()


class TargetSettings(StatesGroup):
    user_id = State()
    target = State()
    confirmation = State()
    
class SexTargetSettings(StatesGroup):
    user_id = State()
    sex_target = State()
    confirmation = State()
    
class CitySettings(StatesGroup):
    user_id = State()
    city = State()
    confirmation = State()
    
class AgeSettings(StatesGroup):
    user_id = State()
    age_from = State()
    age_to = State()
    confirmation = State()
    
    

search_settings_kb = get_keyboard(
    "1",
    "2",
    "3",
    "4",
    "Назад",
    placeholder="Выберите действие",
    sizes=(4, 1)
)
    
    
    
@search_settings_router.message(F.text == "Параметры поиска")
async def search_settings_menu(message: Message, session: AsyncSession):
    filter_params = await get_filter(session, message.from_user.id)
    
    await message.answer(f'Ваши настройки:\n\n<i>Цель</i>: {filter_params.target}\n<i>Город</i>: {filter_params.city}\n<i>Пол</i>: {filter_params.sex_target}\n<i>Возраст</i>: {filter_params.age_from} - {filter_params.age_to}\n\n1. Изменить цель\n2. Изменить город\n3. Изменить пол\n4. Изменить возраст', 
                         reply_markup=search_settings_kb)
    
    
    
    
    
# --------------------------------------- TARGET FSM -----------------------------


@search_settings_router.message(F.text == "1")
async def target_settings(message: Message, state: FSMContext):
    await state.set_state(TargetSettings.target)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Выберите цель", reply_markup=get_callback_btns(
        btns={"Дружба": "Дружба", "Отношения": "Отношения"},
        sizes=(2,)
    ))
    

@search_settings_router.callback_query(StateFilter(TargetSettings.target), F.data)
async def get_target(callback: CallbackQuery, state: FSMContext):
    await state.update_data(target=callback.data)
    await state.set_state(TargetSettings.confirmation)
    await callback.message.edit_text("Подтвердите изменения", reply_markup=get_callback_btns(
        btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
        sizes=(2,)
    ))
    
    
@search_settings_router.callback_query(StateFilter(TargetSettings.confirmation), F.data)
async def target_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if callback.data == "Подтвердить":
        await update_target(session, data["user_id"], data["target"])
    await state.clear()
    
    await callback.message.delete()
    
    filter_params = await get_filter(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: {filter_params.target}\n<i>Город</i>: {filter_params.city}\n<i>Пол</i>: {filter_params.sex_target}\n<i>Возраст</i>: {filter_params.age_from} - {filter_params.age_to}\n\n1. Изменить цель\n2. Изменить город\n3. Изменить пол\n4. Изменить возраст', 
                         reply_markup=search_settings_kb)
    
    
    
# --------------------------------------- CITY FSM -----------------------------


@search_settings_router.message(F.text == "2")
async def city_settings(message: Message, state: FSMContext):
    await state.set_state(CitySettings.city)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Введите город", reply_markup=get_keyboard(
        "Сбросить"
    ))
    

@search_settings_router.message(StateFilter(CitySettings.city), F.text)
async def get_city(message: Message, state: FSMContext):
    if message.text.lower() == "сбросить":
        await state.update_data(city="None")
    elif message.text.lower() not in CITIES_SET:
        await message.answer("Такого города нет, повторите ввод")
        return
    else:
        await state.update_data(city=message.text.capitalize())
    await state.set_state(CitySettings.confirmation)
    await message.answer_sticker("CAACAgIAAxkBAAISCGY15K9Srgqdh2Ksms_n38c69thAAAKPAQACK15TC1JZlsxRJSLCNAQ", reply_markup=ReplyKeyboardRemove())
    await message.answer("Подтвердите изменения", reply_markup=get_callback_btns(
        btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
        sizes=(2,)
    ))
    
    
@search_settings_router.callback_query(StateFilter(CitySettings.confirmation), F.data)
async def city_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if callback.data == "Подтвердить":
        await update_city(session, data["user_id"], data["city"])
    await state.clear()
    
    await callback.message.delete()
    
    filter_params = await get_filter(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: {filter_params.target}\n<i>Город</i>: {filter_params.city}\n<i>Пол</i>: {filter_params.sex_target}\n<i>Возраст</i>: {filter_params.age_from} - {filter_params.age_to}\n\n1. Изменить цель\n2. Изменить город\n3. Изменить пол\n4. Изменить возраст', 
                         reply_markup=search_settings_kb)



# --------------------------------------- SEX TARGET FSM -----------------------------


@search_settings_router.message(F.text == "3")
async def sex_target_settings(message: Message, state: FSMContext):
    await state.set_state(SexTargetSettings.sex_target)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("Кого вы ищете?", reply_markup=get_callback_btns(
        btns={"Девушку": "Девушка", "Парня": "Парень", "Все равно": "Все равно"},
        sizes=(2, 1)
    ))
    
    
@search_settings_router.callback_query(StateFilter(SexTargetSettings.sex_target), F.data)
async def get_sex_target(callback: CallbackQuery, state: FSMContext):
    await state.update_data(sex_target=callback.data)
    await state.set_state(SexTargetSettings.confirmation)
    await callback.message.edit_text("Подтвердите изменения", reply_markup=get_callback_btns(
        btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
        sizes=(2,)
    ))
    
    
@search_settings_router.callback_query(StateFilter(SexTargetSettings.confirmation), F.data)
async def sex_target_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if callback.data == "Подтвердить":
        await update_sex_target(session, data["user_id"], data["sex_target"])
    await state.clear()
    
    await callback.message.delete()
        
    filter_params = await get_filter(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: {filter_params.target}\n<i>Город</i>: {filter_params.city}\n<i>Пол</i>: {filter_params.sex_target}\n<i>Возраст</i>: {filter_params.age_from} - {filter_params.age_to}\n\n1. Изменить цель\n2. Изменить город\n3. Изменить пол\n4. Изменить возраст', 
                         reply_markup=search_settings_kb)
    
    
    
# --------------------------------------- AGE SETTINGS FSM -----------------------------


@search_settings_router.message(F.text == "4")
async def age_settings(message: Message, state: FSMContext):
    await state.set_state(AgeSettings.age_from)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer("С какого возраста вы ищете?", reply_markup=get_keyboard(
        "Сбросить"
    ))
    
    
@search_settings_router.message(StateFilter(AgeSettings.age_from), F.text)
async def get_age_from(message: Message, state: FSMContext):
    if message.text.lower() == "сбросить":
        await state.update_data(age_from=14)
    else:
        if not message.text.isdigit():
            await message.answer("Возраст должен быть числом, повторите ввод")
            return
        elif int(message.text) < 14:
            await message.answer("Возраст должен быть больше 13, повторите ввод")
            return 
        elif int(message.text) > 80:
            await message.answer("Люди столько не живут ;) Возраст должен быть меньше 80 повторите ввод")
            return
        
        await state.update_data(age_from=int(message.text))
    
    await state.set_state(AgeSettings.age_to)
    await message.answer("До какого возраста вы ищете?", reply_markup=get_keyboard(
        "Сбросить"
    ))
    
    
    
@search_settings_router.message(StateFilter(AgeSettings.age_to), F.text)
async def get_age_to(message: Message, state: FSMContext):
    if message.text.lower() == "сбросить":
        await state.update_data(age_to=80)
    else:
        if not message.text.isdigit():
            await message.answer("Возраст должен быть числом, повторите ввод")
            return
        elif int(message.text) < 14:
            await message.answer("Возраст должен быть больше 13, повторите ввод")
            return 
        elif int(message.text) > 80:
            await message.answer("Люди столько не живут ;) Возраст должен быть меньше 80 повторите ввод")
            return
        
        await state.update_data(age_to=int(message.text))
    
    await state.set_state(AgeSettings.confirmation)
    await message.answer_sticker("CAACAgIAAxkBAAISCGY15K9Srgqdh2Ksms_n38c69thAAAKPAQACK15TC1JZlsxRJSLCNAQ", reply_markup=ReplyKeyboardRemove())
    await message.answer("Подтвердите изменения", reply_markup=get_callback_btns(
        btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
        sizes=(2,)
    ))
    
    
@search_settings_router.callback_query(StateFilter(AgeSettings.confirmation), F.data)
async def age_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if callback.data == "Подтвердить":
        await update_age(session, data["user_id"], data["age_from"], data["age_to"])
    await state.clear()
    
    await callback.message.delete()
    
    filter_params = await get_filter(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: {filter_params.target}\n<i>Город</i>: {filter_params.city}\n<i>Пол</i>: {filter_params.sex_target}\n<i>Возраст</i>: {filter_params.age_from} - {filter_params.age_to}\n\n1. Изменить цель\n2. Изменить город\n3. Изменить пол\n4. Изменить возраст', 
                                  reply_markup=search_settings_kb)
        

    

@search_settings_router.message(F.text == "Назад")
async def back(message: Message, state: FSMContext):
    await message.answer("Меню", reply_markup=start_kb)