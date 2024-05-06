from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter

from app.database.dao.uni import get_uni_by_name


# ---------------------------------- FILTER DAO ------------------------------------

# Добавление параметров фильтра
async def add_filter(session: AsyncSession, data: dict[str, str]):
    query = select(Filter).where(Filter.user_id == data["user_id"])
    result = await session.execute(query)
    
    if result.first() is None:
        session.add(Filter(**data))
    else:
        query = update(Filter).where(Filter.user_id == data["user_id"]).values(**data)
        await session.execute(query)
    
    await session.commit()
    
    
async def get_filter(session: AsyncSession, user_id: int):
    query = select(Filter).where(Filter.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()



async def update_target(session: AsyncSession, user_id: int, target: str):
    query = update(Filter).where(Filter.user_id == user_id).values(target=target)
    await session.execute(query)
    await session.commit()
    
    
async def update_sex_target(session: AsyncSession, user_id: int, sex_target: str):
    query = update(Filter).where(Filter.user_id == user_id).values(sex_target=sex_target)
    await session.execute(query)
    await session.commit()
    
    
async def update_city(session: AsyncSession, user_id: int, city: str):
    query = update(Filter).where(Filter.user_id == user_id).values(city=city)
    await session.execute(query)
    await session.commit()
    
    
async def update_age(session: AsyncSession, user_id: int, age_from: int, age_to: int):
    query = update(Filter).where(Filter.user_id == user_id).values(age_from=age_from, age_to=age_to)
    await session.execute(query)
    await session.commit()
    
    
async def update_uni(session: AsyncSession, user_id: int, uni: int):    
    query = update(Filter).where(Filter.user_id == user_id).values(uni_id=uni)
    await session.execute(query)
    await session.commit()



