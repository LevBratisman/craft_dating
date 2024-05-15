from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard

from app.database.dao.user import add_user, get_uni_id_by_user_id
from app.database.dao.project import add_project, get_projects_by_user_id

from app.keyboards.reply import get_menu_keyboard


base_project_router = Router()


del_update_project_kb = get_callback_btns(
    btns={"Изменить": "Изменить", "Удалить": "Удалить"},
)

profile_kb = get_keyboard(
    "🔄",
    "📝",
    "🖼",
    "Мои проекты",
    "Выложить проект",
    "Назад",
    placeholder="Выберите действие",
    sizes=(3, 2, 1)
)
    
    
@base_project_router.message(StateFilter(None), F.text == "Мои проекты")
async def get_my_projects(message: Message, session: AsyncSession):
    projects = await get_projects_by_user_id(session, message.from_user.id)
    for project in projects:
        if project.project_image:
            await message.answer_photo(photo=project.project_image, caption=f'<b>{project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{project.project_requirements}', reply_markup=del_update_project_kb)
        else:
            await message.answer(f'<b>{project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{project.project_requirements}', reply_markup=del_update_project_kb)
    