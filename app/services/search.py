from sqlalchemy.ext.asyncio import AsyncSession

from app.database.dao.user import get_users_by_filter


async def search_users(session: AsyncSession, user_info):
    
    filter_params = {}
        
    for key, value in user_info.items():
        if value and key not in {"id", "created", "updated", "_sa_instance_state"}:
            filter_params[key] = value
            
    print(filter_params)
    
    return await get_users_by_filter(session, filter_params)