from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message

import datetime

from app.database.init import async_session_maker
from app.database.dao.sub import get_subscription_by_user_id
from app.database.dao.sub import delete_subscription

class IsPremiumCheck(BaseMiddleware):
        
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        async with async_session_maker() as session:
            sub = await get_subscription_by_user_id(session, event.from_user.id)
            
            if sub:
                finish_date = sub.finish_date
                if finish_date < datetime.datetime.now():
                    await delete_subscription(session, event.from_user.id)
                    
            
            return await handler(event, data)