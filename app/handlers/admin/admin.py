from aiogram.types import Message
from aiogram import Bot, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from app.keyboards.reply import get_keyboard, get_menu_keyboard
from database.dao.user import get_all_users, get_all_users_id, get_count_users_last_days
from app.filters.admin import IsAdmin
from sqlalchemy.ext.asyncio import AsyncSession


admin_kb = get_keyboard(
    "🔉Сделать рассылку",
    "📊Статистика",
    "⬅️Назад к меню",
)

statistic_kb = get_keyboard(
    "Кол-во пользователей",
    "Прирост пользователей (за последние дни)",
    "⬅️Назад к Админ-панели",
    sizes=(1, 1, 2, )
)


admin_router = Router()
admin_router.message.filter(IsAdmin())

class SendAll(StatesGroup):
    photo = State()
    message = State()
    
    
class GetUsersGain(StatesGroup):
    days = State()


@admin_router.message(Command("admin"))
async def admin_panel(message: Message):
    await message.answer("Вы вошли в админ-панель", reply_markup=admin_kb)
        
    
@admin_router.message(F.text == "⬅️Назад к меню")
async def admin_back(message: Message):
    await message.answer("Вы вернулись в главное меню", reply_markup=await get_menu_keyboard(
            "🔍Искать людей",
            "💕Кто меня лайкнул?",
            "🙎‍♂️Мой профиль",
            "⚙️Параметры поиска",
            placeholder="Выберите действие",
            sizes=(1, ),
            user_id=message.from_user.id
        ))
    
    
@admin_router.message(F.text == "⬅️Назад к Админ-панели")
async def admin_back(message: Message):
    await message.answer("Вы вернулись в Админ-панель", reply_markup=admin_kb)
    
    
# Statistic --------------------------------------------

@admin_router.message(F.text == "📊Статистика")
async def admin_statistic(message: Message):
    await message.answer("📊Статистика", reply_markup=statistic_kb)


@admin_router.message(F.text == "Кол-во пользователей")
async def admin_statistic_users(message: Message, session: AsyncSession):
    await message.answer("Количество пользователей: " + str(len(await get_all_users(session))))
    
    
@admin_router.message(F.text == "Прирост пользователей (за последние дни)")
async def admin_statistic_users_last_day(message: Message, session: AsyncSession, state: FSMContext):
    await state.clear()
    await state.set_state(GetUsersGain.days)
    await message.answer("За какой промежуток времени вы хотите получить статистику? (кол-во дней)")
    
    
@admin_router.message(GetUsersGain.days, F.text)
async def admin_statistic_users_last_days(message: Message, session: AsyncSession, state: FSMContext):
    try:
        days = int(message.text)
    except:
        await message.answer("Неверный формат данных")
        return
    await message.answer("Прирост пользователей за последние " + str(days) + " дня/день/дней: " + str(len(await get_count_users_last_days(session, days))))
    await state.clear()

    
    
# Send all --------------------------------------------

@admin_router.message(F.text == "🔉Сделать рассылку")
async def send_all(message: Message, state: FSMContext):
    await state.set_state(SendAll.photo)
    await message.answer("Теперь отправьте фотографию (либо введите 'n', если пост будет без фотографии)")
    
    
@admin_router.message(SendAll.photo)
async def send_all_photo(message: Message, state: FSMContext):
    try:
        await state.update_data(photo=message.photo[0].file_id)
    except:
        await message.answer("Пост будет без фотографии")
        await state.update_data(photo=None)
    await state.set_state(SendAll.message)
    await message.answer("Теперь введите сообщение")
    
    
@admin_router.message(SendAll.message)
async def send_all_message(message: Message, state: FSMContext, bot: Bot, session: AsyncSession):
    await state.update_data(message=message.text)
    message_data = await state.get_data()
    data = await get_all_users_id(session)
    await message.answer("Рассылка началась")
    if message_data["photo"] is None:
        for user_id in data:
            if user_id > 10_000:
                await bot.send_message(str(user_id), message_data["message"])
    else:
        for user_id in data:
            if user_id > 10_000:
                await bot.send_photo(str(user_id), message_data["photo"], caption=message_data["message"])
    await message.answer("Рассылка завершена")
    await state.clear()