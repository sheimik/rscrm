"""
Репозиторий для визитов
"""
from uuid import UUID
from typing import Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models import Visit, VisitStatus


class VisitRepository(BaseRepository[Visit]):
    """Репозиторий визитов"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Visit)
    
    async def find_by_filters(
        self,
        engineer_id: Optional[UUID] = None,
        object_id: Optional[UUID] = None,
        status: Optional[VisitStatus] = None,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None,
        next_action_due: Optional[bool] = None,  # Для выборок "к прозвону"
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Visit], int]:
        """Поиск с фильтрацией и пагинацией"""
        stmt = select(Visit)
        count_stmt = select(func.count()).select_from(Visit)
        
        conditions = []
        
        if engineer_id:
            conditions.append(Visit.engineer_id == engineer_id)
        
        if object_id:
            conditions.append(Visit.object_id == object_id)
        
        if status:
            conditions.append(Visit.status == status)
        
        if date_from:
            conditions.append(Visit.scheduled_at >= date_from)
        
        if date_to:
            conditions.append(Visit.scheduled_at <= date_to)
        
        # Выборки "к прозвону" (использует индекс next_action_due_at)
        if next_action_due:
            now = datetime.utcnow()
            conditions.append(
                and_(
                    Visit.next_action_due_at.isnot(None),
                    Visit.next_action_due_at <= now,
                )
            )
        
        if conditions:
            where_clause = and_(*conditions)
            stmt = stmt.where(where_clause)
            count_stmt = count_stmt.where(where_clause)
        
        # Получаем общее количество
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Применяем пагинацию и сортировку (использует индекс scheduled_at)
        stmt = stmt.order_by(Visit.scheduled_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total
    
    async def find_by_engineer_and_date_range(
        self,
        engineer_id: UUID,
        date_from: datetime,
        date_to: datetime,
    ) -> list[Visit]:
        """Найти визиты инженера за период (использует составной индекс engineer_id + scheduled_at)"""
        stmt = select(Visit).where(
            and_(
                Visit.engineer_id == engineer_id,
                Visit.scheduled_at >= date_from,
                Visit.scheduled_at <= date_to,
            )
        ).order_by(Visit.scheduled_at.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

