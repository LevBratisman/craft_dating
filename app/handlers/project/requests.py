from aiogram import F, Router
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.keyboards.inline import get_callback_btns
from app.keyboards.reply import get_keyboard

from app.database.dao.user import get_full_user_info, get_request_iterator, set_request_iterator
from app.database.dao.project import add_project, get_project_by_id, get_projects_by_user_id
from app.database.dao.request import get_requests_by_project_id, delete_request_by_id, get_requests_by_creator_id

from app.keyboards.reply import get_menu_keyboard


requests_router = Router()


request_kb = get_keyboard(
    "Вернуться в меню",
    "Дальше"
)

        
@requests_router.message(StateFilter(None), F.text.contains("🔔Заявки"))
async def get_my_requests(message: Message, session: AsyncSession):
    user = await get_full_user_info(session, message.from_user.id)
    await set_request_iterator(session, message.from_user.id, 0)
    if user:
        iter = 0
        requests = await get_requests_by_creator_id(session, message.from_user.id)
        
        if requests:
            await message.answer("Ваши заявки", reply_markup=request_kb)
            request_user = await get_full_user_info(session, requests[iter].user_id)
            project = await get_project_by_id(session, requests[iter].project_id)
            await message.answer_photo(request_user.photo, caption=f"Заявка от @{request_user.username}\nПроект: <b>{project.project_name}</b>", reply_markup=get_callback_btns(btns={"Удалить заявку": f"delete_request_{requests[iter].id}"}))
            await set_request_iterator(session, message.from_user.id, 1)
        else:
            await message.answer("Заявок нет")
            return



@requests_router.message(StateFilter(None), F.text == "Дальше")
async def next_request(message: Message, session: AsyncSession):
    user = await get_full_user_info(session, message.from_user.id)
    if user:
        iter = await get_request_iterator(session, message.from_user.id)
        requests = await get_requests_by_creator_id(session, message.from_user.id)
        if iter == len(requests):
            await set_request_iterator(session, message.from_user.id, 0)
            await message.answer("Заявки закончились", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))
            return
        request_user = await get_full_user_info(session, requests[iter].user_id)
        project = await get_project_by_id(session, requests[iter].project_id)
        await message.answer_photo(request_user.photo, caption=f"Заявка от @{request_user.username}\nПроект: <b>{project.project_name}</b>", reply_markup=get_callback_btns(btns={"Удалить заявку": f"delete_request_{requests[iter].id}"}))
        await set_request_iterator(session, message.from_user.id, iter + 1)
        
                
                
                
@requests_router.callback_query(StateFilter(None), F.data.contains("delete_request_"))
async def delete_request(callback: CallbackQuery, session: AsyncSession, state: FSMContext):
    request_id = int(callback.data.split("_")[2])
    await delete_request_by_id(session, request_id)
    await callback.message.delete()
    if not await get_requests_by_creator_id(session, callback.from_user.id):
        await callback.message.answer("Заявок больше нет", reply_markup=await get_menu_keyboard(user_id=callback.from_user.id))
    
    
    
@requests_router.message(StateFilter(None), F.text == "Вернуться в меню")
async def back_to_menu(message: Message):
    await message.answer("Вы вернулись в меню", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))