from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard

from app.database.dao.user import add_user, get_uni_id_by_user_id
from app.database.dao.project import add_project, get_projects_by_user_id

from app.keyboards.reply import get_menu_keyboard


project_fill_router = Router()


confirm_kb = get_callback_btns(
    btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
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

pass_img_kb = get_keyboard(
    "Пропустить",
)


class ProjectInfo(StatesGroup):
    user_id = State()
    uni_id = State()
    project_name = State()
    project_description = State()
    project_requirements = State()
    project_image = State()
    confirmation = State()
    
    
@project_fill_router.message(StateFilter(None), F.text == "Выложить проект")
async def start_fill_project(message: Message, state: FSMContext, session: AsyncSession):
    current_projects = await get_projects_by_user_id(session, message.from_user.id)
    if len(current_projects) == 1:
        await message.answer("Для того чтобы публиковать более одного проекта купите подписку")
        return
    else:
        await state.set_state(ProjectInfo.project_name)
        await message.answer_sticker("CAACAgIAAxkBAAISQWZEfFQfwsYBLa88sfzVUqLox3VKAAKRAQACK15TC92mC_kqIE5PNQQ", reply_markup=ReplyKeyboardRemove())
        await message.answer("Введите название проекта")
    
    
    
@project_fill_router.message(StateFilter(ProjectInfo.project_name), F.text)
async def get_project_name(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(project_name=message.text)
    await state.set_state(ProjectInfo.project_description)
    await message.answer("Кратко опишите ваш проект")
    
        
    
@project_fill_router.message(StateFilter(ProjectInfo.project_description), F.text)
async def get_project_desc(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(project_description=message.text)
    await state.set_state(ProjectInfo.project_requirements)
    await message.answer("Кого вы ищите? Расскажите о требованиях")
    
    
@project_fill_router.message(StateFilter(ProjectInfo.project_requirements), F.text)
async def get_project_req(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(project_requirements=message.text)
    await state.set_state(ProjectInfo.project_image)
    await message.answer("Прикрепите свою фотографию (необязательно)", reply_markup=pass_img_kb)
    
    
    
@project_fill_router.message(StateFilter(ProjectInfo.project_image), F.photo)
async def get_project_img(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(project_image=message.photo[-1].file_id)
    await state.set_state(ProjectInfo.confirmation)
    data = await state.get_data()
    await message.answer("Подтвердите изменения", reply_markup=ReplyKeyboardRemove())
    await message.answer_photo(photo=data["project_image"], caption=f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}', reply_markup=confirm_kb)
    
    
@project_fill_router.message(StateFilter(ProjectInfo.project_image), F.text)
async def get_project_img(message: Message, state: FSMContext, session: AsyncSession):
    await state.update_data(project_image=None)
    await state.set_state(ProjectInfo.confirmation)
    data = await state.get_data()
    await message.answer("Подтвердите изменения", reply_markup=ReplyKeyboardRemove())
    await message.answer(f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}', reply_markup=confirm_kb)
    
    
@project_fill_router.callback_query(StateFilter(ProjectInfo.confirmation), F.data)
async def get_project_confirm(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await callback.message.delete()
    if callback.data == "Подтвердить":
        
        
        
        await state.update_data(user_id=callback.from_user.id)
        uni_id = await get_uni_id_by_user_id(session, callback.from_user.id)
        await state.update_data(uni_id=uni_id)
        data = await state.get_data()
        
        await add_project(session, data)
        await state.clear()
        await callback.message.answer("Ваш проект успешно опубликован", reply_markup=profile_kb)
    else:
        await state.clear()
        await callback.message.answer("Вы отменили публикацию", reply_markup=profile_kb)
    