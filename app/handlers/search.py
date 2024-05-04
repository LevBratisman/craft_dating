from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_user_by_user_id, add_liked_users

from app.keyboards.reply import get_keyboard

from app.handlers.base import register_kb, start_kb
from app.services.search import search_users


search_router = Router()


search_kb = get_keyboard(
    "🧡",
    "👎",
    "🚪",
    placeholder="Выберите действие",
    sizes=(4,)
)

is_like_kb = get_keyboard(
    "💛",
    "🙈"
)

exit_from_liked_kb = get_keyboard(
    "Поехали",
    "Меню"
)


is_like_check_kb = get_keyboard(
    "Показать",
    sizes=(1,)
)


target_users = []
liked_users = []

iter = 0
liked_users_iter = 0

@search_router.message(StateFilter(None), F.text == "Искать людей")
async def start_search(message: Message, session: AsyncSession):
    global target_users, iter
    await message.answer("🔍")
    user = await get_user_by_user_id(session, message.from_user.id)
    print(user)
    if user:
        search_params = {
            "target": user.target,
            "sex_target": user.sex_target,
            "user_id": user.user_id
        }
        
        target_users = await search_users(session, search_params)
        
        if target_users:
            try:
                await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb)
            except IndexError:
                iter = 0
                await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb)
        else:
            await message.answer("По вашему запросу ничего не найдено")
        
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
        
        
@search_router.message(StateFilter(None), F.text == "🚪")
async def back(message: Message):
    await message.answer("Меню", reply_markup=start_kb)
    
    

@search_router.message(F.text.in_(["👎", "🧡"]))
async def next_user(message: Message, session: AsyncSession, bot: Bot):
    global target_users, iter
    print(iter)
    if message.text == "🧡":
        target_user = target_users[iter]
        if target_user:
            if target_user.liked_users is None:
                liked_users = f"{message.from_user.id},"
                await add_liked_users(session, target_user.user_id, liked_users)
                await bot.send_message(chat_id=target_users[iter].user_id, text="Кто-то вами заинтересовался!", reply_markup=is_like_check_kb)
            else:
                liked_users = target_user.liked_users.split(",")
                if message.from_user.id not in liked_users:
                    liked_users = ",".join(liked_users) + f"{message.from_user.id},"
                    await add_liked_users(session, target_user.user_id, liked_users)
                    await bot.send_message(chat_id=target_users[iter].user_id, text="Кто-то вами заинтересовался!", reply_markup=is_like_check_kb)
        
    
    if iter == len(target_users) - 1:
        iter = 0
        await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb)
    else:
        iter += 1
        await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb)
    
    
    
@search_router.message(F.text == "Показать")
async def show_liked_users(message: Message, session: AsyncSession):
    global liked_users, liked_users_iter
    liked_users_iter = 0
    user = await get_user_by_user_id(session, message.from_user.id)
    liked_users = user.liked_users.split(",")
    liked_user = await get_user_by_user_id(session, liked_users[liked_users_iter])
    await message.answer_photo(liked_user.photo, caption=f'Вы заинтересовали:\n\n{liked_user.name}, {liked_user.age}\nГород: {liked_user.city}\n\n{liked_user.description}', reply_markup=is_like_kb)
    
    
@search_router.message(F.text == "💛")
async def like(message: Message, session: AsyncSession, bot: Bot):
    global liked_users, liked_users_iter
    user = await get_user_by_user_id(session, message.from_user.id)
    liked_users_self_list = user.liked_users.split(",")
    liked_user = await get_user_by_user_id(session, liked_users_self_list[liked_users_iter])
    await message.answer(f"Приятного общения! @{liked_user.username}")
    await bot.send_photo(chat_id=liked_user.user_id, 
                         photo=user.photo, 
                         caption=f'Взаимный интерес! Приятного общения c @{user.username}\n\n{user.name}, {user.age}\nГород: {user.city}\n\n{user.description}', 
                         reply_markup=get_keyboard("Продолжить просмотр анкет"))
    if liked_users_iter == len(liked_users) - 2:
        if len(liked_users_self_list) == 2:
            await add_liked_users(session, user.user_id, "")
        else:
            liked_user_list = liked_user.liked_users.split(",")
            liked_user_list.remove(str(user.user_id))
            await add_liked_users(session, liked_user.user_id, ','.join(liked_user_list))
        liked_users_iter = 0
        liked_users = []
        await message.answer("Пока все, идем дальше!", reply_markup=exit_from_liked_kb)
    else:
        liked_users_iter += 1
        liked_user = await get_user_by_user_id(session, liked_users[liked_users_iter])
        await message.answer_photo(liked_user.photo, caption=f'Вы заинтересовали:\n\n{liked_user.name}, {liked_user.age}\nГород: {liked_user.city}\n\n{liked_user.description}', reply_markup=is_like_kb)
        
    
@search_router.message(F.text == "🙈")
async def next_liked_user(message: Message, session: AsyncSession):
    global liked_users, liked_users_iter
    user = await get_user_by_user_id(session, message.from_user.id)
    liked_users_self_list = user.liked_users.split(",")
    liked_user = await get_user_by_user_id(session, liked_users_self_list[liked_users_iter])
    if liked_users_iter == len(liked_users) - 2:
        if len(liked_users_self_list) == 2:
            await add_liked_users(session, user.user_id, "")
        else:
            liked_user_list = liked_user.liked_users.split(",")
            liked_user_list.remove(str(user.user_id))
            await add_liked_users(session, liked_user.user_id, ','.join(liked_user_list))
        liked_users_iter = 0
        liked_users = []
        await message.answer("Пока все, продолжить поиск?", reply_markup=exit_from_liked_kb)
    else:
        liked_users_iter += 1
        liked_user = await get_user_by_user_id(session, liked_users[liked_users_iter])
        await message.answer_photo(liked_user.photo, caption=f'Вы заинтересовали:\n\n{liked_user.name}, {liked_user.age}\nГород: {liked_user.city}\n\n{liked_user.description}', reply_markup=is_like_kb)
        
        
        
@search_router.message(F.text == "Поехали")
async def continue_search(message: Message, session: AsyncSession):
    await start_search(message, session)
    
@search_router.message(F.text == "Меню")
async def continue_search(message: Message, session: AsyncSession):
    await message.answer("Вы вернулись в главное меню!", reply_markup=start_kb)

@search_router.message(F.text == "Продолжить просмотр анкет")
async def continue_search(message: Message, session: AsyncSession):
    await start_search(message, session)