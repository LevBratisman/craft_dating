from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_users_by_target


async def search_users(session: AsyncSession, params: dict):
    return await get_users_by_target(session, params["target"], params["sex_target"], params["user_id"])