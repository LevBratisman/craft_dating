from aiogram import F, Router, Bot
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.filters import StateFilter
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.database.dao.user import set_iterator, get_iterator, get_full_user_info, get_project_iterator, set_project_iterator, get_uni_id_by_user_id
from app.database.dao.filter import get_filter
from app.database.dao.like import add_liked_user, get_like
from app.database.dao.project import get_project_by_id, get_projects_by_uni_id
from app.database.dao.request import add_request, get_requests_by_project_id

from app.keyboards.reply import get_keyboard
from app.keyboards.inline import get_callback_btns

from app.handlers.base import register_kb
from app.services.search import search_users

from app.keyboards.reply import get_menu_keyboard


search_project_router = Router()


class SendRequest(StatesGroup):
    project_id = State()
    text = State()


project_search_kb = get_keyboard(
    "Далее",
    "🚪",
    placeholder="Выберите действие",
    sizes=(2, )
)


@search_project_router.message(StateFilter(None), F.text.in_(["💡Искать проекты", "Далее"]))
async def start_search_project(message: Message, session: AsyncSession):
    
    user = await get_full_user_info(session, message.from_user.id)
    
    if user:
        target_projects = await get_projects_by_uni_id(session, user.uni_id)
        iter = user.project_iterator
        
        if target_projects:
            await message.answer("🔍", reply_markup=project_search_kb)
            try:
                current_project = target_projects[iter]
                bid_keyboard = get_callback_btns(
                    btns={"Подать заявку": f"request_{current_project.id}"},
                )
                if current_project.project_image:
                    await message.answer_photo(current_project.project_image, caption=f'<b>{current_project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{current_project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{current_project.project_description}', reply_markup=bid_keyboard)
                else:
                    await message.answer(f'<b>{current_project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{current_project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{current_project.project_description}', reply_markup=bid_keyboard)
                await set_iterator(session, message.from_user.id, iter + 1)
            except IndexError:
                iter = 0
                current_project = target_projects[iter]
                bid_keyboard = get_callback_btns(
                    {"Подать заявку": f"request_{current_project.id}"},
                )
                if current_project.project_image:
                    await message.answer_photo(current_project.project_image, caption=f'<b>{current_project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{current_project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{current_project.project_description}', reply_markup=bid_keyboard)
                else:
                    await message.answer(f'<b>{current_project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{current_project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{current_project.project_description}', reply_markup=bid_keyboard)
                await set_iterator(session, message.from_user.id, 1)
        else:
            await message.answer("По вашему запросу ничего не найдено")
        
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
    await asyncio.shield(session.close())

        
        
        
@search_project_router.message(StateFilter(None), F.text == "🚪")
async def back(message: Message):
    await message.answer("Меню", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))
    
    
    
@search_project_router.callback_query(StateFilter(None), F.data.contains("request_"))
async def bid(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    project_id = int(callback.data.split("_")[1])
    await state.set_state(SendRequest.text)
    await state.update_data(project_id=project_id)
    
    if await get_requests_by_project_id(session, project_id):
        await callback.answer("Вы уже подали заявку")
        await state.clear()
        return
    
    await callback.answer("Подача заявки")
    
    await callback.message.answer("Введите текст заявки", reply_markup=ReplyKeyboardRemove())
    
    
    
@search_project_router.message(StateFilter(SendRequest.text), F.text)
async def get_text(message: Message, state: FSMContext, session: AsyncSession, bot: Bot):
    await state.update_data(text=message.text)
    data = await state.get_data()
    project_id = data.pop("project_id")
    project = await get_project_by_id(session, project_id)
    
    data = {
        "user_id": message.from_user.id,
        "project_id": project_id,
        "creator_id": project.user_id,
        "text": message.text
    }
    await add_request(session, data)
    await state.clear()
    await message.answer("Заявка отправлена")
    await bot.send_message(project.user_id, "Новая заявка на проект!")
    await start_search_project(message, session)
    