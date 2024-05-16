from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, InputMediaPhoto
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard

from app.database.dao.user import add_user, get_uni_id_by_user_id
from app.database.dao.project import add_project, get_project_by_id, get_projects_by_user_id, delete_project_by_id, update_project_by_id

from app.keyboards.reply import get_menu_keyboard


base_project_router = Router()


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

confirm_kb = get_callback_btns(
    btns={"Подтвердить": "Подтвердить", "Отменить": "Отменить"},
)


class UpdateProject(StatesGroup):
    project_id = State()
    project_name = State()
    project_description = State()
    project_requirements = State()
    project_image = State()
    project_confirm = State()
    
    
    
    
@base_project_router.message(StateFilter(None), F.text == "Мои проекты")
async def get_my_projects(message: Message, session: AsyncSession):
    projects = await get_projects_by_user_id(session, message.from_user.id)
    
    if projects:
        for project in projects:
            if project.project_image:
                await message.answer_photo(photo=project.project_image, caption=f'<b>{project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{project.project_requirements}', reply_markup=get_callback_btns(btns={"Удалить проект": f"delete_project_{project.id}", "Обновить проект": f"update_project_{project.id}"}))
            else:
                await message.answer(f'<b>{project.project_name}</b>\n\n<b>ОПИСАНИЕ</b>\n{project.project_description}\n\n<b>КОГО ИЩЕМ?</b>\n{project.project_requirements}', reply_markup=get_callback_btns(btns={"Удалить проект": f"delete_project_{project.id}", "Обновить проект": f"update_project_{project.id}"}))
    else:
        await message.answer("У вас нет опубликованных проектов")
    
    

@base_project_router.callback_query(StateFilter(None), F.data.contains("delete_project_"))
async def delete_project(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    project_id = int(callback.data.split("_")[2])
    await delete_project_by_id(session, project_id)
    await callback.answer("Проект был удален")
    await callback.message.delete()
    await callback.message.answer("Проект был удален", reply_markup=profile_kb)
    
    
# ----------------------------------------UPDATE PROJECT FSM---------------------------------------
    
@base_project_router.callback_query(StateFilter(None), F.data.contains("update_project_"))
async def update_project(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    project_id = int(callback.data.split("_")[2])
    
    current_project = await get_project_by_id(session, project_id)
    
    await state.set_state(UpdateProject.project_name)
    await callback.answer("Обновление проекта")
    
    print(await state.get_state())
    
    await state.update_data(project_id=project_id)
    await state.update_data(project_name=current_project.project_name)
    await state.update_data(project_description=current_project.project_description)
    await state.update_data(project_requirements=current_project.project_requirements)
    await state.update_data(project_image=current_project.project_image)
    
    await callback.message.answer("Напишите новое название проекта", reply_markup=get_keyboard("Не менять"))
    
    print(await state.get_state())
    
    
@base_project_router.message(StateFilter(UpdateProject.project_name), F.text)
async def keep_old_name(message: Message, state: FSMContext):
    if message.text != "Не менять":
        await state.update_data(project_name=message.text)
    await state.set_state(UpdateProject.project_description)
    await message.answer("Введите новое описание проекта")
    
    
    
@base_project_router.message(StateFilter(UpdateProject.project_description), F.text)
async def keep_old_desc(message: Message, state: FSMContext):
    if message.text != "Не менять":
        await state.update_data(project_description=message.text)
    await state.set_state(UpdateProject.project_requirements)
    await message.answer("Введите новые требования к проекту")
    
        
    
@base_project_router.message(StateFilter(UpdateProject.project_requirements), F.text)
async def keep_old_req(message: Message, state: FSMContext):
    if message.text != "Не менять":
        await state.update_data(project_requirements=message.text)
    await state.set_state(UpdateProject.project_image)
    await message.answer("Прикрепите новое изображение", reply_markup=get_keyboard("Не менять", "Удалить изображение", sizes=(1, )))
    
        
    
@base_project_router.message(StateFilter(UpdateProject.project_image), F.photo)
@base_project_router.message(StateFilter(UpdateProject.project_image), F.text)
async def keep_old_img(message: Message, state: FSMContext):
    
    if message.text == "Удалить изображение":
        await state.update_data(project_image=None)
    elif message.text != "Не менять":
        await state.update_data(project_image=message.photo[-1].file_id)
    
    await state.set_state(UpdateProject.project_confirm)
    data = await state.get_data()
    
    await message.answer("Подтвердите изменения", reply_markup=ReplyKeyboardRemove())
    
    if data["project_image"]:
        await message.answer_photo(photo=data["project_image"], caption=f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}', reply_markup=confirm_kb)
    else:
        await message.answer(f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}', reply_markup=confirm_kb)        
        
        
@base_project_router.callback_query(StateFilter(UpdateProject.project_confirm))
async def confirm_update_project(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    
    if callback.data == "Подтвердить":
        data = await state.get_data()
        project_id = data.pop("project_id")
        
        image = InputMediaPhoto(media=data["project_image"], caption=f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}') if data["project_image"] else None
        
        await update_project_by_id(session=session, project_id=project_id, data=data)
        await callback.answer("Обновлено!")
        await state.clear()
        if not data["project_image"]:
            await callback.message.edit_text(f'<b>{data["project_name"]}</b>\n\n<b>ОПИСАНИЕ</b>\n{data["project_description"]}\n\n<b>КОГО ИЩЕМ?</b>\n{data["project_requirements"]}', 
                                             reply_markup=get_callback_btns(btns={"Удалить проект": f"delete_project_{project_id}", "Обновить проект": f"update_project_{project_id}"}))
        else:
            await callback.message.edit_media(media=image, 
                                              reply_markup=get_callback_btns(btns={"Удалить проект": f"delete_project_{project_id}", "Обновить проект": f"update_project_{project_id}"}))
            
        await callback.message.answer("Ваш проект успешно обновлен", reply_markup=profile_kb)
    else:
        await state.clear()
        await callback.message.delete()
        await callback.answer("Отмена обновления")
        await callback.message.answer("Отмена", reply_markup=profile_kb)
        
        
    await state.clear()