"""
Репозиторий для объектов
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models import Object, ObjectStatus


class ObjectRepository(BaseRepository[Object]):
    """Репозиторий объектов"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Object)
    
    async def find_by_filters(
        self,
        city_id: Optional[UUID] = None,
        district_id: Optional[UUID] = None,
        status: Optional[ObjectStatus] = None,
        responsible_user_id: Optional[UUID] = None,
        search_query: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Object], int]:
        """Поиск с фильтрами и пагинацией"""
        stmt = select(Object)
        count_stmt = select(func.count()).select_from(Object)
        
        if city_id:
            stmt = stmt.where(Object.city_id == city_id)
            count_stmt = count_stmt.where(Object.city_id == city_id)
        
        if district_id:
            stmt = stmt.where(Object.district_id == district_id)
            count_stmt = count_stmt.where(Object.district_id == district_id)
        
        if status:
            stmt = stmt.where(Object.status == status)
            count_stmt = count_stmt.where(Object.status == status)
        
        if responsible_user_id:
            stmt = stmt.where(Object.responsible_user_id == responsible_user_id)
            count_stmt = count_stmt.where(Object.responsible_user_id == responsible_user_id)
        
        if search_query:
            search_pattern = f"%{search_query.lower()}%"
            stmt = stmt.where(Object.address.ilike(search_pattern))
            count_stmt = count_stmt.where(Object.address.ilike(search_pattern))
        
        # Получаем общее количество
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Применяем пагинацию (использует индекс updated_at)
        stmt = stmt.order_by(Object.updated_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total

