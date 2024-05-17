import datetime
from aiogram import F, Bot, Router
from aiogram.types import Message, CallbackQuery, LabeledPrice, ShippingQuery, PreCheckoutQuery
from aiogram.filters import CommandStart

from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao.sub import add_subscription, delete_subscription, get_subscription_by_user_id
from app.keyboards.reply import get_keyboard, get_menu_keyboard
from app.keyboards.inline import get_callback_btns

from app.common.text import premium_text

from app.config import settings


# from tests.test_data import data_user, data_filter


premium_router = Router()


premium_kb = get_keyboard(
    "💎МЕСЯЦ",
    "💎ГОД",
    "Отменить подписку",
    "Назад",
    sizes=(2, 1, 1, )
)
    
    
@premium_router.message(F.text == "💎Premium")
async def premium(message: Message, session: AsyncSession):
    await message.answer(premium_text, reply_markup=premium_kb)
        
        
@premium_router.message(F.text == "1m")
async def minute(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
        return        
    current_date = datetime.datetime.now()
    finish_date = current_date + datetime.timedelta(minutes=1)
    
    data = {
        "user_id": message.from_user.id,
        "finish_date": finish_date,
        "subscription_type": "month"
    }

    await add_subscription(session, data)
    await message.answer("Вы успешно оформили подписку на минуту!", reply_markup=await get_menu_keyboard(user_id=message.from_user.id))

        
@premium_router.message(F.text == "💎МЕСЯЦ")
async def month(message: Message, session: AsyncSession, bot: Bot):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
        return
    
    PRICE = LabeledPrice(label='Premium-подписка', amount=199 * 100)
    TOKEN = settings.PAYMENT_TOKEN
    #await add_order_db(data)
    await bot.send_invoice(
                            message.from_user.id,
                            title='1 Месяц',
                            description='Оплата',
                            provider_token=TOKEN,
                            currency='rub',
                            photo_url='https://i.pinimg.com/originals/4d/a0/bb/4da0bbb45aa953339a7e7cd9535884f5.jpg',
                            photo_height=900,  # !=0/None, иначе изображение не покажется
                            photo_width=900,
                            photo_size=200,
                            is_flexible=False,  # True если конечная цена зависит от способа доставки
                            prices=[PRICE],
                            start_parameter='time-machine-example',
                            payload='some-invoice-payload-for-our-internal-use',
                            request_timeout=60
    )
        
    await message.answer("Оплатили?", reply_markup=get_callback_btns(btns={"Оплатил": "month"}))    
    
    
        
        
@premium_router.callback_query(F.data == "month")
async def active_month(callback: CallbackQuery, session: AsyncSession):
    current_date = datetime.datetime.now()
    finish_date = current_date + datetime.timedelta(days=30)
    
    data = {
        "user_id": callback.from_user.id,
        "finish_date": finish_date,
        "subscription_type": "month"
    }

    await add_subscription(session, data)
    await callback.message.edit_text("Вы успешно оформили подписку на месяц!")
        
        
        
@premium_router.message(F.text == "💎ГОД")
async def month(message: Message, session: AsyncSession, bot: Bot):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await message.answer("Вы уже оформили подписку")
        return
    
    PRICE = LabeledPrice(label='Premium-подписка', amount=999 * 100)
    TOKEN = settings.PAYMENT_TOKEN
    #await add_order_db(data)
    await bot.send_invoice(
                            chat_id=message.from_user.id,
                            title='1 год',
                            description='Оплата',
                            provider_token=TOKEN,
                            currency='rub',
                            photo_url='https://i.pinimg.com/originals/4d/a0/bb/4da0bbb45aa953339a7e7cd9535884f5.jpg',
                            photo_height=1280,  # !=0/None, иначе изображение не покажется
                            photo_width=1026,
                            photo_size=1000,
                            is_flexible=False,  # True если конечная цена зависит от способа доставки
                            prices=[PRICE],
                            start_parameter='time-machine-example',
                            payload='some-invoice-payload-for-our-internal-use',
                            request_timeout=60
    )
    
    await message.answer("Оплатили?", reply_markup=get_callback_btns(btns={"Оплатил": "year"}))
        


@premium_router.callback_query(F.data == "year")
async def active_month(callback: CallbackQuery, session: AsyncSession):
    current_date = datetime.datetime.now()
    finish_date = current_date + datetime.timedelta(days=365)
    
    data = {
        "user_id": callback.from_user.id,
        "finish_date": finish_date,
        "subscription_type": "year"
    }

    await add_subscription(session, data)
    await callback.message.edit_text("Вы успешно оформили подписку на год!")



@premium_router.message(F.text == "Отменить подписку")
async def refuse_subscription(message: Message, session: AsyncSession):
    sub = await get_subscription_by_user_id(session, message.from_user.id)
    if sub:
        await delete_subscription(session, message.from_user.id)
        await message.answer("Вы отменили подписку!")
    else:
        await message.answer("Вы еще не оформили подписку!")
        
        
        
# -------------------------- Payment ------------------------- #
    
    
@premium_router.shipping_query(F.shipping_query)
async def shipping(shipping_query: ShippingQuery):
    await shipping_query.answer(ok=True)
    print("SHIPPING: ")
    print(shipping_query)
    
    
@premium_router.pre_checkout_query(F.pre_checkout_query)
async def pre_checkout_query(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    print("Подтверждение оплаты")
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
    print(pre_checkout_query)