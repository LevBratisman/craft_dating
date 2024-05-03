from sqlalchemy import delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import User


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
        await session.commit()
    else:
        query = update(User).where(User.user_id == data["user_id"]).values(**data)
        await session.execute(query)
        await session.commit()
        

# Получение всех пользователей
async def get_all_users_by_craft(session: AsyncSession, craft: str):
    query = select(User).where(User.craft == craft)
    result = await session.execute(query)
    return result.scalars().all()


# Получение id пользователя по user_id
async def get_user_by_user_id(session: AsyncSession, user_id: int):
    query = select(User).where(User.user_id == user_id)
    result = await session.execute(query)
    return result.scalars().first()


async def del_user_by_user_id(session: AsyncSession, user_id: int):
    query = delete(User).where(User.user_id == user_id)
    await session.execute(query)
    await session.commit()



# ---------------------------------- REVIEW DAO ------------------------------------

# # Получение всех отзывов
# async def get_all_reviews(session: AsyncSession):
#     query = select(Review)
#     result = await session.execute(query)
#     return result.scalars().all() 

# # Получение отзывов по лимиту
# async def get_reviews_by_limit(session: AsyncSession, limit: int):
#     query = select(Review).limit(limit)
#     result = await session.execute(query)
#     return result.scalars().all()

# # Добавление отзыва
# async def add_review(session: AsyncSession, user_id: int, text: str):
#     session.add(Review(user_id=user_id, text=text))
#     await session.commit()



