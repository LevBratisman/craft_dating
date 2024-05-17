from datetime import datetime
from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Subscription, Filter, Project


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
    await reset_target_filter(session, user_id)
    await delete_extra_projects(session, user_id)
    await session.execute(query)
    await session.commit()
        
    
async def reset_target_filter(session: AsyncSession, user_id: int):
    query = update(Filter).where(Filter.user_id == user_id).values(target=None)
    await session.execute(query)
    await session.commit()
    
    
async def delete_extra_projects(session: AsyncSession, user_id: int):
    
    query = select(Project.id).where(Project.user_id == user_id)
    result = await session.execute(query)
    projects = result.scalars().all()
    
    if len(projects) < 2:
        return
    else:
        for i in range(len(projects) - 1):
            query = delete(Project).where(Project.id == projects[i])
            await session.execute(query)
            await session.commit()