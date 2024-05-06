from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import Uni


# ---------------------------------- UNI DAO ------------------------------------


async def add_uni(session: AsyncSession, data: dict[str, str]):
    query = select(Uni).where(Uni.name == data["name"])
    result = await session.execute(query)
    
    if result.first() is None:
        session.add(Uni(**data))
    else:
        query = update(Uni).where(Uni.name == data["name"]).values(**data)
        await session.execute(query)
    
    await session.commit()
    
    
async def get_uni_by_name(session: AsyncSession, name: str):
    query = select(Uni).where(Uni.name == name)
    result = await session.execute(query)
    return result.scalars().first()


async def get_uni_by_id(session: AsyncSession, uni_id: int):
    query = select(Uni).where(Uni.id == uni_id)
    result = await session.execute(query)
    return result.scalars().first()