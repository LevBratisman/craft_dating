from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter, Request


# ---------------------------------- Request DAO ------------------------------------

async def add_request(session: AsyncSession, data: dict[str, str]):
    session.add(Request(**data))
    await session.commit()
    
    
async def get_requests_by_user_id(session: AsyncSession, user_id: int):
    query = select(Request).where(Request.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_requests_by_project_id(session: AsyncSession, project_id: int):
    query = select(Request).where(Request.project_id == project_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_requests_by_creator_id(session: AsyncSession, creator_id: int):
    query = select(Request).where(Request.creator_id == creator_id)
    result = await session.execute(query)
    return result.scalars().all()


async def delete_request_by_id(session: AsyncSession, request_id: int):
    query = delete(Request).where(Request.id == request_id)
    await session.execute(query)
    await session.commit()
    
    
async def delete_requests_by_project_id(session: AsyncSession, project_id: int):
    query = delete(Request).where(Request.project_id == project_id)
    await session.execute(query)
    await session.commit()