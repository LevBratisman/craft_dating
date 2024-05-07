from sqlalchemy.ext.asyncio import AsyncSession

from time import time

from app.database.dao.user import get_users_by_filter

# from app.database.init import async_session_maker

# import asyncio


async def search_users(session: AsyncSession, user_info):
    
    filter_params = {}
        
    for key, value in user_info.items():
        if value and key not in {"id", "created", "updated", "_sa_instance_state"}:
            filter_params[key] = value
            
    print(filter_params)
    
    return await get_users_by_filter(session, filter_params)


# params = {'user_id': 700457035, 'name': 'Лев', 'username': 'bratisman', 'age': 20, 'sex': 'Парень', 'photo': 'AgACAgIAAxkBAAIgqmY5z--rKtEhZ0SnP8G6Kw8Ih0LqAAK02zEbXAS5Sb_8kdfEe6XwAQADAgADeAADNQQ', 'description': ' ', 'iterator': 4, 'uni_id': 2, 'uni_name': 'Московский политех', 'uni_city': 'Москва', 'target': 'Отношения', 'sex_target': 'Девушка'}

# i = 0
# start = time()
# session = async_session_maker()
# while i < 1000:
#     result = asyncio.run(search_users(session, params))
#     i += 1
# print(time() - start)