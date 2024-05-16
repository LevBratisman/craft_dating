import datetime
from sqlalchemy import and_, delete, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter, Uni


# ---------------------------------- USER DAO ------------------------------------

# Добавление пользователя
async def add_user(
    session: AsyncSession,
    data: dict[str, str]
):
    query = select(User).where(User.user_id == data["user_id"])
    result = await session.execute(query)
    
    if result.first() is None:
        session.add(User(**data))
    else:
        query = update(User).where(User.user_id == data["user_id"]).values(**data)
        await session.execute(query)
    
    await session.commit()
                

# Получение всех пользователей
async def get_all_users(session: AsyncSession):
    query = select(User)
    result = await session.execute(query)
    return result.scalars().all()


async def get_all_users_id(session: AsyncSession):
    query = select(User.user_id)
    result = await session.execute(query)
    return result.scalars().all()


async def get_count_users_last_days(session: AsyncSession, days: int):
    query = select(User.id).where(User.created >= (datetime.datetime.now() - datetime.timedelta(days=days)))
    result = await session.execute(query)
    return result.scalars().all()


async def get_uni_id_by_user_id(session, user_id):
    return select(User.uni_id).where(User.user_id == user_id)


# Получение id пользователя по user_id
async def get_user_by_user_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def get_users_by_filter(session: AsyncSession, params: dict):
    
    User_Filter_view = select(
        User.user_id,
        User.name, 
        User.age, 
        User.uni_id, 
        User.sex,
        User.photo, 
        User.description,
        Filter.sex_target,
        Filter.target,
        Uni.name.label('uni_name'),
        Uni.city,
    ).join(Filter, Filter.user_id == User.user_id).join(Uni, Uni.id == User.uni_id).subquery()
        
    if params["sex_target"] == "Все равно":
        query = select(User_Filter_view).where(and_(
            User_Filter_view.c.user_id != params["user_id"],
            User_Filter_view.c.uni_id == params["uni_id"],
            or_(
                User_Filter_view.c.sex_target == params["sex"],
                User_Filter_view.c.sex_target == "Все равно"
            )
        ))
    else:
        query = select(User_Filter_view).where(and_(
            User_Filter_view.c.user_id != params["user_id"],
            User_Filter_view.c.uni_id == params["uni_id"],
            User_Filter_view.c.sex == params["sex_target"],
            or_(
                User_Filter_view.c.sex_target == params["sex"],
                User_Filter_view.c.sex_target == "Все равно"
            )
        ))

        
    result = await session.execute(query)
    return result.mappings().all()



async def update_user_description(session: AsyncSession, user_id: int, description: str):
    query = update(User).where(User.user_id == user_id).values(description=description)
    await session.execute(query)
    await session.commit()
    
    
async def update_user_photo(session: AsyncSession, user_id: int, photo: str):
    query = update(User).where(User.user_id == user_id).values(photo=photo)
    await session.execute(query)
    await session.commit()
    
    
async def get_iterator(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first().iterator
    
    
async def set_iterator(session: AsyncSession, user_id: int, iterator: int):
    query = update(User).where(User.user_id == user_id).values(iterator=iterator)
    await session.execute(query)
    await session.commit()
    
    
async def get_like_iterator(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first().like_iterator
    
    
async def set_like_iterator(session: AsyncSession, user_id: int, like_iterator: int):
    query = update(User).where(User.user_id == user_id).values(like_iterator=like_iterator)
    await session.execute(query)
    await session.commit()
    
    
    
async def get_project_iterator(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first().project_iterator
    
    
async def set_project_iterator(session: AsyncSession, user_id: int, project_iterator: int):
    query = update(User).where(User.user_id == user_id).values(project_iterator=project_iterator)
    await session.execute(query)
    await session.commit()
    
    
async def get_request_iterator(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first().request_iterator
    
    
async def set_request_iterator(session: AsyncSession, user_id: int, request_iterator: int):
    query = update(User).where(User.user_id == user_id).values(request_iterator=request_iterator)
    await session.execute(query)
    await session.commit()
    

async def delete_user(session: AsyncSession, user_id: int):
    query = delete(User).where(User.user_id == user_id)
    await session.execute(query)
    await session.commit()
    
    
    
async def get_full_user_info(session: AsyncSession, user_id: int):
    result = await session.execute(
        select(
            User.id,
            User.user_id,
            User.name,
            User.username,
            User.age,
            User.sex,
            User.photo,
            User.description,
            User.iterator,
            User.like_iterator,
            User.project_iterator,
            User.request_iterator,
            User.target.label('target_desc'),
            Uni.id.label('uni_id'),
            Uni.name.label('uni_name'),
            Uni.city.label('uni_city'),
            Filter.target,
            Filter.sex_target
            ).join(
            Filter, User.user_id == Filter.user_id
        ).join(
            Uni, Filter.uni_id == Uni.id
        ).where(User.user_id == user_id)
    )
    return result.mappings().one()

