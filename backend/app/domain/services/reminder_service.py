"""
Сервис для напоминаний (использует индекс next_action_due_at)
"""
from datetime import datetime, timedelta
from typing import list
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import Visit
from app.infrastructure.db.repositories.visit_repository import VisitRepository
from sqlalchemy import select, and_


class ReminderService:
    """Сервис напоминаний о следующих действиях"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.visit_repo = VisitRepository(session)
    
    async def get_reminders_due(
        self,
        engineer_id: str | None = None,
        days_ahead: int = 7,
    ) -> list[Visit]:
        """
        Получить визиты с напоминаниями "к прозвону"
        
        Использует индекс ix_visits_next_action_due_at для быстрого поиска.
        """
        now = datetime.utcnow()
        deadline = now + timedelta(days=days_ahead)
        
        stmt = select(Visit).where(
            and_(
                Visit.next_action_due_at.isnot(None),
                Visit.next_action_due_at >= now,
                Visit.next_action_due_at <= deadline,
            )
        )
        
        if engineer_id:
            stmt = stmt.where(Visit.engineer_id == engineer_id)
        
        # Использует составной индекс (engineer_id, scheduled_at) если указан engineer_id
        stmt = stmt.order_by(Visit.next_action_due_at.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def get_overdue_reminders(
        self,
        engineer_id: str | None = None,
    ) -> list[Visit]:
        """Получить просроченные напоминания (использует индекс)"""
        now = datetime.utcnow()
        
        stmt = select(Visit).where(
            and_(
                Visit.next_action_due_at.isnot(None),
                Visit.next_action_due_at < now,
                Visit.status != "DONE",  # Не показываем завершённые
            )
        )
        
        if engineer_id:
            stmt = stmt.where(Visit.engineer_id == engineer_id)
        
        stmt = stmt.order_by(Visit.next_action_due_at.asc())
        
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

