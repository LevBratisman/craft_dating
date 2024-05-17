from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard

from app.database.dao.filter import get_filter, update_target, update_city, update_sex_target, update_uni
from app.database.dao.uni import get_uni_by_id, get_uni_by_name
from app.database.dao.user import get_full_user_info

from app.filters.admin import IsPremium

from app.handlers.fill import pop_uni_kb
from app.database.dao.user import get_user_by_user_id


search_settings_router = Router()


class TargetSettings(StatesGroup):
    user_id = State()
    target = State()
    confirmation = State()
    
class SexTargetSettings(StatesGroup):
    user_id = State()
    sex_target = State()
    confirmation = State()
    
class UniSettings(StatesGroup):
    user_id = State()
    uni = State()
    confirmation = State()
    
# class AgeSettings(StatesGroup):
#     user_id = State()
#     age_from = State()
#     age_to = State()
#     confirmation = State()
    
    

search_settings_kb = get_keyboard(
    "1",
    "2",
    "3",
    "Назад",
    placeholder="Выберите действие",
    sizes=(3, 1)
)
    
    
    
@search_settings_router.message(F.text == "⚙️Параметры поиска")
async def search_settings_menu(message: Message, session: AsyncSession):
    
    user_info = await get_full_user_info(session, message.from_user.id)
    await message.answer(f'Ваши настройки:\n\n<i>Цель</i>: <b>{user_info["target"]}</b>\n<i>ВУЗ</i>: <b>{user_info["uni_name"]}</b>\n<i>Кого ищу (пол)</i>: <b>{user_info["sex_target"]}</b>\n\n1. Изменить цель (💎Premium)\n2. Изменить ВУЗ\n3. Изменить пол', 
                         reply_markup=search_settings_kb)
    
    
    
    
    
# --------------------------------------- TARGET FSM -----------------------------


@search_settings_router.message(IsPremium(), F.text == "1")
async def target_settings(message: Message, state: FSMContext):
    await state.set_state(TargetSettings.target)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer_sticker("CAACAgIAAxkBAAISDGY5Jbyq2OLMjQRrwS9QSRKQER6QAAKBAQACK15TC14KbD5sAAF4tDUE", reply_markup=ReplyKeyboardRemove())
    await message.answer("Что вы ищите?", reply_markup=get_callback_btns(
            btns={"Дружбу": "Дружба", "Отношения": "Отношения", "Как пойдет": "Как пойдет", "Сбросить": "None"},
            sizes=(2, 1, 1)
        ))
    
    
@search_settings_router.message(F.text == "1")
async def reject_target_settings(message: Message, state: FSMContext):
    await message.answer("Доступно только для премиум аккаунтов")
    
    

@search_settings_router.callback_query(StateFilter(TargetSettings.target), F.data)
async def get_target(callback: CallbackQuery, state: FSMContext):
    if callback.data == "None":
        await state.update_data(target=None)
    else:
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
    
    user_info = await get_full_user_info(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: <b>{user_info["target"]}</b>\n<i>ВУЗ</i>: <b>{user_info["uni_name"]}</b>\n<i>Кого ищу (пол)</i>: <b>{user_info["sex_target"]}</b>\n\n1. Изменить цель (💎Premium)\n2. Изменить ВУЗ\n3. Изменить пол', 
                         reply_markup=search_settings_kb)
    
    
    
# --------------------------------------- UNI FSM -----------------------------


@search_settings_router.message(F.text == "2")
async def city_settings(message: Message, state: FSMContext):
    await state.set_state(UniSettings.uni)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer_sticker("CAACAgIAAxkBAAISDGY5Jbyq2OLMjQRrwS9QSRKQER6QAAKBAQACK15TC14KbD5sAAF4tDUE", reply_markup=ReplyKeyboardRemove())
    await message.answer("Выберите ВУЗ", reply_markup=pop_uni_kb)
    

@search_settings_router.callback_query(StateFilter(UniSettings.uni), F.data)
async def get_uni(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    if callback.data == "none":
        await callback.message.edit_text(f"К сожалению, сервис пока поддерживает только эти университеты\nВыберите один из списка", reply_markup=pop_uni_kb)
        return
    else:
        uni = await get_uni_by_name(session, callback.data)
        await state.update_data(uni=uni.id)
    await state.set_state(UniSettings.confirmation)
    await callback.message.edit_text("Подтвердите изменения", reply_markup=get_callback_btns(
        btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
        sizes=(2,)
    ))
    
    
@search_settings_router.callback_query(StateFilter(UniSettings.confirmation), F.data)
async def city_confirmation(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()

    if callback.data == "Подтвердить":
        await update_uni(session, data["user_id"], data["uni"])
    await state.clear()
    
    await callback.message.delete()
    
    user_info = await get_full_user_info(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: <b>{user_info["target"]}</b>\n<i>ВУЗ</i>: <b>{user_info["uni_name"]}</b>\n<i>Кого ищу (пол)</i>: <b>{user_info["sex_target"]}</b>\n\n1. Изменить цель (💎Premium)\n2. Изменить ВУЗ\n3. Изменить пол', 
                         reply_markup=search_settings_kb)



# --------------------------------------- SEX TARGET FSM -----------------------------


@search_settings_router.message(F.text == "3")
async def sex_target_settings(message: Message, state: FSMContext):
    await state.set_state(SexTargetSettings.sex_target)
    await state.update_data(user_id=int(message.from_user.id))
    await message.answer_sticker("CAACAgIAAxkBAAISDGY5Jbyq2OLMjQRrwS9QSRKQER6QAAKBAQACK15TC14KbD5sAAF4tDUE", reply_markup=ReplyKeyboardRemove())
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
        
    user_info = await get_full_user_info(session, data["user_id"])
    await callback.message.answer(f'Ваши настройки:\n\n<i>Цель</i>: <b>{user_info["target"]}</b>\n<i>ВУЗ</i>: <b>{user_info["uni_name"]}</b>\n<i>Кого ищу (пол)</i>: <b>{user_info["sex_target"]}</b>\n\n1. Изменить цель (💎Premium)\n2. Изменить ВУЗ\n3. Изменить пол', 
                         reply_markup=search_settings_kb)
    
