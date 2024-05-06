from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter


# ---------------------------------- LIKE DAO ------------------------------------


async def get_like(session: AsyncSession, user_id: int):
    query = select(Like).where(Like.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def add_like_stats(session: AsyncSession, data: dict[str, str]):
    query = select(Like).where(Like.user_id == data["user_id"])
    result = await session.execute(query)
    
    if result.first() is None:
        session.add(Like(**data))
    else:
        query = update(Like).where(Like.user_id == data["user_id"]).values(**data)
        await session.execute(query)
    
    await session.commit()
    
    
    
async def add_liked_user(session: AsyncSession, user_id: int, liked_users: str):
    query = update(Like).where(Like.user_id == user_id).values(liked_users_id=liked_users)
    await session.execute(query)
    await session.commit()
    
    