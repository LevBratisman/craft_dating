from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter, CommandStart
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_user_by_user_id, add_liked_user, get_filter, get_like, set_iterator, get_iterator, get_like_iterator, set_like_iterator

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

liked_users_iter = 0

@search_router.message(StateFilter(None), F.text == "Искать людей")
async def start_search(message: Message, session: AsyncSession):
    global target_users
    
    await message.answer("🔍")
    user_filter = await get_filter(session, message.from_user.id)
    user = await get_user_by_user_id(session, message.from_user.id)
    
    iter = user.iterator
    
    if user_filter:

        filter_params = {}
        
        for key, value in user_filter.__dict__.items():
            if value and key not in {"id", "created", "updated", "_sa_instance_state"}:
                filter_params[key] = value
                
        filter_params["sex"] = user.sex
        
        print(filter_params)
        
        target_users = await search_users(session, filter_params)
        print(target_users)
        
        if target_users:
            try:
                await set_iterator(session, message.from_user.id, user.iterator + 1)
                iter += 1
                await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb)
            except IndexError:
                await set_iterator(session, message.from_user.id, 0)
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
    global target_users
    
    iter = await get_iterator(session, message.from_user.id)
    
    print(iter)
    
    if not target_users:
        await start_search(message, session)
        return
    
    try:
        if message.text == "🧡":
            
            target_user = target_users[iter]
            
            # is Bot checking
            if target_user.user_id < 10_000:
                pass
            else:
                like_stats_of_target_user = await get_like(session, target_user.user_id)
                
                if like_stats_of_target_user:
                    if like_stats_of_target_user.liked_users_id is '':
                        liked_users_id = f"{message.from_user.id}"
                        await add_liked_user(session, target_user.user_id, liked_users_id)
                        await bot.send_message(chat_id=target_user.user_id, text="Кто-то вами заинтересовался!", reply_markup=is_like_check_kb)
                    else:
                        liked_users_id = like_stats_of_target_user.liked_users_id.split(",")
                        print(liked_users_id)
                        if str(message.from_user.id) not in liked_users_id:
                            liked_users_id = ",".join(liked_users_id) + f",{message.from_user.id}"
                            await add_liked_user(session, target_user.user_id, liked_users_id)
                            await bot.send_message(chat_id=target_user.user_id, text="Кто-то вами заинтересовался!", reply_markup=is_like_check_kb)
                            
        if iter >= len(target_users) - 1:
            iter = 0
        else:
            iter += 1
        await set_iterator(session, message.from_user.id, iter)
        await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb) 
    except IndexError:
        iter = 0
        await set_iterator(session, message.from_user.id, 0)
        await message.answer_photo(target_users[iter].photo, caption=f'{target_users[iter].name}, {target_users[iter].age}\nГород: {target_users[iter].city}\n\n{target_users[iter].description}', reply_markup=search_kb) 
    
    
    
@search_router.message(F.text == "Показать")
async def show_liked_users(message: Message, session: AsyncSession):
    global liked_users
    liked_users_iter = await get_like_iterator(session, message.from_user.id)
    user_like_stats = await get_like(session, message.from_user.id)
    
    liked_users_id = user_like_stats.liked_users_id.split(",")
    liked_user = await get_user_by_user_id(session, int(liked_users_id[liked_users_iter]))
    
    await message.answer_photo(liked_user.photo, caption=f'Вы заинтересовали:\n\n{liked_user.name}, {liked_user.age}\nГород: {liked_user.city}\n\n{liked_user.description}', reply_markup=is_like_kb)
    
    
    
@search_router.message(F.text.in_(["💛", "🙈"]))
async def like(message: Message, session: AsyncSession, bot: Bot):
    global liked_users
    
    user = await get_user_by_user_id(session, message.from_user.id)
    user_like_stats = await get_like(session, message.from_user.id)
    
    liked_users_iter = user.like_iterator
    print(liked_users_iter)
    
    liked_users = user_like_stats.liked_users_id.split(",")
    try:
        liked_user = await get_user_by_user_id(session, liked_users[liked_users_iter])
    except IndexError:
        await add_liked_user(session, user.user_id, "")
        await set_like_iterator(session, message.from_user.id, 0)
        liked_users = []
        await message.answer("Пока все, продолжить поиск?", reply_markup=exit_from_liked_kb)
    
    
    if message.text == "💛":
        await message.answer(f"Приятного общения! @{liked_user.username}")
        await bot.send_photo(chat_id=liked_user.user_id, 
                            photo=user.photo, 
                            caption=f'Взаимный интерес! Приятного общения c @{user.username}\n\n{user.name}, {user.age}\nГород: {user.city}\n\n{user.description}', 
                            reply_markup=get_keyboard("Продолжить просмотр анкет"))
    
    if liked_users_iter == len(liked_users) - 1:
        await add_liked_user(session, user.user_id, "")
        await set_like_iterator(session, message.from_user.id, 0)
        liked_users = []
        await message.answer("Пока все, продолжить поиск?", reply_markup=exit_from_liked_kb)
    else:
        liked_users_iter += 1
        await set_like_iterator(session, message.from_user.id, liked_users_iter)
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