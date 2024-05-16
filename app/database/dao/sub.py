from datetime import datetime
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Subscription


# ---------------------------------- SUB DAO ------------------------------------

async def get_subscription_by_user_id(session: AsyncSession, user_id: int):
    query = select(Subscription).where(Subscription.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def add_subscription(session: AsyncSession, data: dict[str, str]):
    session.add(Subscription(**data))
    await session.commit()
    

async def delete_subscription(session: AsyncSession, user_id: int):
    query = delete(Subscription).where(Subscription.user_id == user_id)
    await session.execute(query)
    await session.commit()