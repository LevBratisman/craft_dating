from aiogram import F, Router, Bot
from aiogram.types import Message
from aiogram.filters import StateFilter
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao.user import set_iterator, get_iterator, get_full_user_info
from app.database.dao.filter import get_filter
from app.database.dao.like import add_liked_user, get_like

from app.keyboards.reply import get_keyboard

from app.handlers.base import register_kb
from app.services.search import search_users

from app.keyboards.reply import get_menu_keyboard


search_router = Router()


search_kb = get_keyboard(
    "❤️",
    "👎",
    "🚪",
    placeholder="Выберите действие",
    sizes=(4,)
)

exit_from_liked_kb = get_keyboard(
    "Смотреть анкеты",
    "Меню"
)


is_like_check_kb = get_keyboard(
    "Показать",
    "Позже",
    sizes=(2,)
)


@search_router.message(StateFilter(None), F.text == "🔍Искать людей")
async def start_search(message: Message, session: AsyncSession):
    
    await message.answer("🔍")
    iter = await get_iterator(session, message.from_user.id)
    
    user_info = await get_full_user_info(session, message.from_user.id)
    
    if user_info:
        
        target_users = await search_users(session, user_info)
        
        if target_users:
            try:
                await set_iterator(session, message.from_user.id, iter + 1)
                iter += 1
                await message.answer_photo(target_users[iter].photo, caption=f'🎴{target_users[iter].name}, {target_users[iter].age}, {target_users[iter].city}\n🏛<b>{target_users[iter].uni_name}</b>\n🔍<b>{target_users[iter].target}</b>\n\n{target_users[iter].description}', reply_markup=search_kb)
            except IndexError:
                await set_iterator(session, message.from_user.id, 0)
                iter = 0
                await message.answer_photo(target_users[iter].photo, caption=f'🎴{target_users[iter].name}, {target_users[iter].age}, {target_users[iter].city}\n🏛<b>{target_users[iter].uni_name}</b>\n🔍<b>{target_users[iter].target}</b>\n\n{target_users[iter].description}', reply_markup=search_kb)
        else:
            await message.answer("По вашему запросу ничего не найдено")
        
    else:
        await message.answer("Вы ещё не заполнили анкету", reply_markup=register_kb)
        
        
        
@search_router.message(StateFilter(None), F.text == "🚪")
async def back(message: Message):
    await message.answer("Меню", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                    "💕Кто меня лайкнул?", 
                                                                    "🙎‍♂️Мой профиль", 
                                                                    "⚙️Параметры поиска",
                                                                    placeholder="Выберите действие", 
                                                                    sizes=(1, ), 
                                                                    user_id=message.from_user.id))
    
    

@search_router.message(F.text.in_(["👎", "❤️"]))
async def next_user(message: Message, session: AsyncSession, bot: Bot):
    
    iter = await get_iterator(session, message.from_user.id)
    
    user_info = await get_full_user_info(session, message.from_user.id)
    
    
    if user_info:
        target_users = await search_users(session, user_info)
    
    if not target_users:
        await message.answer("По вашему запросу ничего не найдено", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                               "💕Кто меня лайкнул?", 
                                                                                               "🙎‍♂️Мой профиль", 
                                                                                               "⚙️Параметры поиска",
                                                                                               placeholder="Выберите действие", 
                                                                                               sizes=(1, ), 
                                                                                               user_id=message.from_user.id))
        return
    
    try:
        if message.text == "❤️":
            
            target_user = target_users[iter]            
            
            # is Bot checking
            if target_user.user_id < 10_000:
                pass
            else:
                like_stats_of_target_user = await get_like(session, target_user.user_id)
                # like_stats = await get_like(session, message.from_user.id)
                # like_stats_list = like_stats.liked_users_id.split(",")
                
                # if like_stats_of_target_user and str(target_user.user_id) not in like_stats_list:
                if like_stats_of_target_user:
                    if like_stats_of_target_user.liked_users_id is '':
                        liked_users_id = f"{message.from_user.id}"
                        await add_liked_user(session, target_user.user_id, liked_users_id)
                        await bot.send_message(chat_id=target_user.user_id, text="Кто-то вами заинтересовался!")
                    else:
                        liked_users_id = like_stats_of_target_user.liked_users_id.split(",")
                        if str(message.from_user.id) not in liked_users_id:
                            liked_users_id = ",".join(liked_users_id) + f",{message.from_user.id}"
                            await add_liked_user(session, target_user.user_id, liked_users_id)
                            await bot.send_message(chat_id=target_user.user_id, text="Кто-то вами заинтересовался!")
                            
        if iter >= len(target_users) - 1:
            iter = 0
        else:
            iter += 1
        await set_iterator(session, message.from_user.id, iter)
        await message.answer_photo(target_users[iter].photo, caption=f'🎴{target_users[iter].name}, {target_users[iter].age}, {target_users[iter].city}\n🏛<b>{target_users[iter].uni_name}</b>\n🔍<b>{target_users[iter].target}</b>\n\n{target_users[iter].description}', reply_markup=search_kb)
    except IndexError:
        await set_iterator(session, message.from_user.id, 0)
        iter = 0
        await message.answer_photo(target_users[iter].photo, caption=f'🎴{target_users[iter].name}, {target_users[iter].age}, {target_users[iter].city}\n🏛<b>{target_users[iter].uni_name}</b>\n🔍<b>{target_users[iter].target}</b>\n\n{target_users[iter].description}', reply_markup=search_kb) 
    
    
    
# @search_router.message(F.text == "Показать")
# async def show_liked_users(message: Message, session: AsyncSession, state: FSMContext):
#     await state.clear()
#     liked_users_iter = await get_like_iterator(session, message.from_user.id)
#     user_like_stats = await get_like(session, message.from_user.id)
    
#     liked_users_id = user_like_stats.liked_users_id.split(",")
#     liked_user = await get_full_user_info(session, int(liked_users_id[liked_users_iter]))
    
#     await message.answer_photo(liked_user["photo"], caption=f'Вы заинтересовали:\n\n🎴{liked_user["name"]}, {liked_user["age"]}, {liked_user["uni_city"]}\n🏛<b>{liked_user["uni_name"]}</b>\n🔍<b>{liked_user["target"]}</b>\n\n{liked_user.description}', reply_markup=is_like_kb)
    
    
    
# @search_router.message(F.text.in_(["💛", "🙈"]))
# async def like(message: Message, session: AsyncSession, bot: Bot):
    
#     user = await get_full_user_info(session, message.from_user.id)
#     user_like_stats = await get_like(session, message.from_user.id)
    
#     liked_users_iter = user["like_iterator"]
#     print(liked_users_iter)
    
#     liked_users = user_like_stats.liked_users_id.split(",")
#     try:
#         liked_user = await get_full_user_info(session, liked_users[liked_users_iter])
#     except IndexError:
#         await add_liked_user(session, user["user_id"], "")
#         await set_like_iterator(session, message.from_user.id, 0)
#         await message.answer("Пока все, смотреть анкеты дальше?", reply_markup=exit_from_liked_kb)
    
    
#     if message.text == "💛":
#         await message.answer(f"Приятного общения! @{liked_user.username}")
#         await bot.send_photo(chat_id=liked_user.user_id, 
#                             photo=user.photo, 
#                             caption=f'Взаимный интерес! Приятного общения c @{user.username}\n\n🎴{user["name"]}, {user["age"]}, {user["uni_city"]}\n🏛<b>{user["uni_name"]}</b>\n🔍<b>{user["target"]}</b>\n\n{user["description"]}', 
#                             reply_markup=exit_from_liked_kb)
    
#     if liked_users_iter == len(liked_users) - 1:
#         await add_liked_user(session, user.user_id, "")
#         await set_like_iterator(session, message.from_user.id, 0)
#         await message.answer("Пока все, продолжить поиск?", reply_markup=exit_from_liked_kb)
#     else:
#         liked_users_iter += 1
#         await set_like_iterator(session, message.from_user.id, liked_users_iter)
#         liked_user = await get_full_user_info(session, liked_users[liked_users_iter])
#         await message.answer_photo(liked_user["photo"], caption=f'Вы заинтересовали:\n\n🎴{liked_user["name"]}, {liked_user["age"]}, {liked_user["uni_city"]}\n🏛{liked_user["uni_name"]}\n🔍<b>{user["target"]}</b>\n\n{liked_user["description"]}', reply_markup=is_like_kb)
        
    

# @search_router.message(F.text.in_(["Продолжить просмотр анкет", "Поехали", "Меню", "Позже"]))
# async def continue_search(message: Message, session: AsyncSession):
    
#     iter = await get_iterator(session, message.from_user.id)
    
#     user_info = await get_full_user_info(session, message.from_user.id)
#     if user_info:
#         target_users = await search_users(session, user_info)
        
#     if iter == 0:
#         await set_iterator(session, message.from_user.id, len(target_users) - 1)
#     else:
#         await set_iterator(session, message.from_user.id, iter - 1)
        
#     if message.text == "Меню":
#         await message.answer("Вы вернулись в главное меню!", reply_markup=await get_menu_keyboard("Искать людей", 
#                                                                                                "Кто меня лайкнул?", 
#                                                                                                "Мой профиль", 
#                                                                                                "Параметры поиска",
#                                                                                                placeholder="Выберите действие", 
#                                                                                                sizes=(2, 2), 
#                                                                                                user_id=message.from_user.id))
#     else:
#         await start_search(message, session)