from aiogram.filters import Filter

from app.config import settings


import datetime

from app.database.init import async_session_maker
from app.database.dao.sub import get_subscription_by_user_id
from app.database.dao.sub import delete_subscription


class IsAdmin(Filter):
    async def __call__(self, message):
        return message.from_user.id == settings.ADMIN_ID
    
    
class IsPremium(Filter):
    async def __call__(self, message):
        async with async_session_maker() as session:
            sub = await get_subscription_by_user_id(session, message.from_user.id)
            
            if sub:
                finish_date = sub.finish_date
                if finish_date > datetime.datetime.now():
                    return True
                else:
                    await delete_subscription(session, message.from_user.id)
                    return False
            else:
                return False
    