from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao import get_users_by_filter


async def search_users(session: AsyncSession, params: dict):
    return await get_users_by_filter(session, params)