from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import asyncio

from app.database.dao.user import get_full_user_info

from app.keyboards.reply import get_keyboard, get_menu_keyboard

from app.handlers.search import start_search
from app.services.search import search_users

from app.database.dao.like import get_like, add_liked_user
from app.database.dao.user import get_like_iterator, set_like_iterator, get_iterator, set_iterator


like_router = Router()

search_kb = get_keyboard(
    "❤️",
    "👎",
    "🚪",
    placeholder="Выберите действие",
    sizes=(4,)
)

is_like_kb = get_keyboard(
    "💞",
    "🚫"
)

exit_from_liked_kb = get_keyboard(
    "Смотреть анкеты",
    "Меню"
)



@like_router.message(F.text.contains("💕Кто меня лайкнул?"))
async def show_liked_users(message: Message, session: AsyncSession):
    liked_users_iter = await get_like_iterator(session, message.from_user.id)
    user_like_stats = await get_like(session, message.from_user.id)
    
    liked_users_id = user_like_stats.liked_users_id.split(",")
    if liked_users_id[liked_users_iter] == "":
        await message.answer("Вы ещё не заинтересовали людей")
        return
    liked_user = await get_full_user_info(session, int(liked_users_id[liked_users_iter]))
    
    await message.answer_photo(liked_user["photo"], caption=f'Вы заинтересовали:\n\n🎴{liked_user["name"]}, {liked_user["age"]}, {liked_user["uni_city"]}\n🏛<b>{liked_user["uni_name"]}</b>\n🔍<b>{liked_user["target"]}</b>\n\n{liked_user.description}', reply_markup=is_like_kb)
    
    
    
@like_router.message(F.text.in_(["💞", "🚫"]))
async def like(message: Message, session: AsyncSession, bot: Bot):
    
    user = await get_full_user_info(session, message.from_user.id)
    user_like_stats = await get_like(session, message.from_user.id)
    
    liked_users_iter = user["like_iterator"]
    
    liked_users = user_like_stats.liked_users_id.split(",")
    try:
        liked_user = await get_full_user_info(session, liked_users[liked_users_iter])
    except IndexError:
        await add_liked_user(session, user["user_id"], "")
        await set_like_iterator(session, message.from_user.id, 0)
        await message.answer("На этом все", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                "💕Кто меня лайкнул?", 
                                                                                "🙎‍♂️Мой профиль", 
                                                                                "⚙️Параметры поиска",
                                                                                placeholder="Выберите действие", 
                                                                                sizes=(1, ), 
                                                                                user_id=message.from_user.id))
    
    
    if message.text == "💞":
        await message.answer(f"Приятного общения c @{liked_user.username}!")
        await bot.send_photo(chat_id=liked_user.user_id, 
                            photo=user.photo, 
                            caption=f'Взаимный интерес! Приятного общения c @{user.username}\n\n🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n🏛<b>{user["uni_name"]}</b>\n🔍<b>{user["target"]}</b>\n\n{user["description"]}', 
                            reply_markup=exit_from_liked_kb)
    
    if liked_users_iter == len(liked_users) - 1:
        await add_liked_user(session, user.user_id, "")
        await set_like_iterator(session, message.from_user.id, 0)
        await message.answer("На этом все", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                "💕Кто меня лайкнул?", 
                                                                                "🙎‍♂️Мой профиль", 
                                                                                "⚙️Параметры поиска",
                                                                                placeholder="Выберите действие", 
                                                                                sizes=(1, ), 
                                                                                user_id=message.from_user.id))
    else:
        liked_users_iter += 1
        await set_like_iterator(session, message.from_user.id, liked_users_iter)
        liked_user = await get_full_user_info(session, liked_users[liked_users_iter])
        await message.answer_photo(liked_user["photo"], caption=f'Вы заинтересовали:\n\n🎴{liked_user["name"]}, {liked_user["age"]}, {liked_user["uni_city"]}\n🏛{liked_user["uni_name"]}\n🔍<b>{user["target"]}</b>\n\n{liked_user["description"]}', reply_markup=is_like_kb)
        
    

@like_router.message(F.text.in_(["Меню", "Смотреть анкеты"]))
async def continue_search(message: Message, session: AsyncSession, state: FSMContext):
    
    await state.clear()
        
    if message.text == "Меню":
        await message.answer("Вы вернулись в главное меню!", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                               "💕Кто меня лайкнул?", 
                                                                                               "🙎‍♂️Мой профиль", 
                                                                                               "⚙️Параметры поиска",
                                                                                               placeholder="Выберите действие", 
                                                                                               sizes=(1, ), 
                                                                                               user_id=message.from_user.id))
    else:
        iter = await get_iterator(session, message.from_user.id)
    
        user_info = await get_full_user_info(session, message.from_user.id)
        if user_info:
            target_users = await search_users(session, user_info)
            
        if iter == 0:
            await set_iterator(session, message.from_user.id, len(target_users) - 1)
        else:
            await set_iterator(session, message.from_user.id, iter - 1)
            
        await start_search(message, session)
        await asyncio.shield(session.close())

# Помоги пожалуйста! Мне необходимо загрузить Чат-бота(написанного на aiogram3) на VPS-сервер. Детали - используется webhook
# Webhook адрес API на FastAPI, которое передает обновления от телеграма локально в бота. Как мне необходимо настроить сервер и какие шаги я должен предпринять?