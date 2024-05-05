from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User, Like, Filter


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
        User.city, 
        User.sex,
        User.photo, 
        User.description,
        Filter.sex_target,
        Filter.target
    ).join(Filter, Filter.user_id == User.user_id).subquery()
        
    if params["city"] != "None":
        if params["sex_target"] == "Все равно":
            query = select(User_Filter_view).where(
                User_Filter_view.c.age.between(params["age_from"], params["age_to"]),
                User_Filter_view.c.user_id != params["user_id"],
                User_Filter_view.c.sex_target == params["sex"] or User_Filter_view.c.sex_target == "Все равно",
                User_Filter_view.c.target == params["target"],
                User_Filter_view.c.city == params["city"]
            )
        else:
            query = select(User_Filter_view).where(
                User_Filter_view.c.age.between(params["age_from"], params["age_to"]),
                User_Filter_view.c.user_id != params["user_id"],
                User_Filter_view.c.sex == params["sex_target"],
                User_Filter_view.c.sex_target == params["sex"] or User_Filter_view.c.sex_target == "Все равно",
                User_Filter_view.c.target == params["target"],
                User_Filter_view.c.city == params["city"]
            )
    else:
        if params["sex_target"] == "Все равно":
            query = select(User_Filter_view).where(
                User_Filter_view.c.age.between(params["age_from"], params["age_to"]),
                User_Filter_view.c.user_id != params["user_id"],
                User_Filter_view.c.sex_target == params["sex"] or User_Filter_view.c.sex_target == "Все равно",
                User_Filter_view.c.target == params["target"],
            )
        else:
            query = select(User_Filter_view).where(
                User_Filter_view.c.age.between(params["age_from"], params["age_to"]),
                User_Filter_view.c.user_id != params["user_id"],
                User_Filter_view.c.sex == params["sex_target"],
                User_Filter_view.c.sex_target == params["sex"] or User_Filter_view.c.sex_target == "Все равно",
                User_Filter_view.c.target == params["target"],
            )
        
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
    

async def delete_user(session: AsyncSession, user_id: int):
    query = delete(User).where(User.user_id == user_id)
    await session.execute(query)
    await session.commit()



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
    
    
