from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter, Project


# ---------------------------------- PROJECT DAO ------------------------------------

async def add_project(session: AsyncSession, data: dict[str, str]):
    session.add(Project(**data))
    await session.commit()
    
async def get_projects_by_user_id(session: AsyncSession, user_id: int):
    query = select(Project).where(Project.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().all()

async def get_project_by_id(session: AsyncSession, project_id: int):
    query = select(Project).where(Project.id == project_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_projects_by_uni_id(session: AsyncSession, uni_id: int):
    query = select(Project).where(Project.uni_id == uni_id)
    result = await session.execute(query)
    return result.scalars().all()