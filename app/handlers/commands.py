import asyncio
from aiogram.types import Message
from aiogram import Router, F, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from sqlalchemy.ext.asyncio import AsyncSession


from app.handlers.search import start_search
from app.keyboards.reply import get_menu_keyboard
from app.common.text import help_text

cmd_router = Router()


class SendFeedback(StatesGroup):
    feedback = State()


@cmd_router.message(Command("menu"))
async def back(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Меню", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                    "💕Кто меня лайкнул?", 
                                                                    "🙎‍♂️Мой профиль", 
                                                                    "⚙️Параметры поиска",
                                                                    placeholder="Выберите действие", 
                                                                    sizes=(1, ), 
                                                                    user_id=message.from_user.id))
        

# Отправка отзыва -----------------------------------------

@cmd_router.message(Command("feedback"))
async def cmd_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Вы можете отправить отзыв в специальный чат @unidatefeed", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                               "💕Кто меня лайкнул?", 
                                                                                               "🙎‍♂️Мой профиль", 
                                                                                               "⚙️Параметры поиска",
                                                                                               placeholder="Выберите действие", 
                                                                                               sizes=(1, ), 
                                                                                               user_id=message.from_user.id))
    
    
# ---------------------------------------------------------------
    
    
@cmd_router.message(Command("search"))
async def cmd_search(message: Message, state: FSMContext, session: AsyncSession):
    await state.clear()
    await start_search(message, session)
    
    
@cmd_router.message(Command("contacts"))
async def cmd_feedback(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("По всем вопросам обращайтесь к @bratisman", reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                                               "💕Кто меня лайкнул?", 
                                                                                               "🙎‍♂️Мой профиль", 
                                                                                               "⚙️Параметры поиска",
                                                                                               placeholder="Выберите действие", 
                                                                                               sizes=(1, ), 
                                                                                               user_id=message.from_user.id))
    
    
@cmd_router.message(Command("help"))
async def cmd_search(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(help_text, reply_markup=await get_menu_keyboard("🔍Искать людей", 
                                                                        "💕Кто меня лайкнул?", 
                                                                        "🙎‍♂️Мой профиль", 
                                                                        "⚙️Параметры поиска",
                                                                        placeholder="Выберите действие", 
                                                                        sizes=(1, ), 
                                                                        user_id=message.from_user.id))