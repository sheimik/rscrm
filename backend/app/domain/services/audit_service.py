"""
Сервис аудита для записи всех изменений
"""
from uuid import UUID
from typing import Optional, Any, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import AuditLog, ActionType, User
from app.core.logging_config import get_logger

logger = get_logger(__name__)


class AuditService:
    """Сервис аудита"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def log_action(
        self,
        action: ActionType,
        entity_type: str,
        entity_id: UUID,
        actor_id: Optional[UUID],
        before: Optional[dict[str, Any]] = None,
        after: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Записать действие в аудит"""
        logger.debug(
            "Logging audit action",
            action=action.value,
            entity_type=entity_type,
            entity_id=str(entity_id),
            actor_id=str(actor_id) if actor_id else None,
        )
        
        audit_log = AuditLog(
            actor_id=actor_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            before_json=before,
            after_json=after,
            ip_address=ip_address,
            user_agent=user_agent,
            occurred_at=datetime.utcnow(),
        )
        
        self.session.add(audit_log)
        await self.session.flush()
        
        logger.info(
            "Audit action logged",
            audit_log_id=str(audit_log.id),
            action=action.value,
            entity_type=entity_type,
            entity_id=str(entity_id),
            actor_id=str(actor_id) if actor_id else None,
        )
        
        return audit_log
    
    async def log_create(
        self,
        entity_type: str,
        entity_id: UUID,
        actor_id: Optional[UUID],
        after: dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Записать создание"""
        return await self.log_action(
            action=ActionType.CREATE,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            before=None,
            after=after,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    async def log_update(
        self,
        entity_type: str,
        entity_id: UUID,
        actor_id: Optional[UUID],
        before: dict[str, Any],
        after: dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Записать обновление"""
        return await self.log_action(
            action=ActionType.UPDATE,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            before=before,
            after=after,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    async def log_delete(
        self,
        entity_type: str,
        entity_id: UUID,
        actor_id: Optional[UUID],
        before: dict[str, Any],
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Записать удаление"""
        return await self.log_action(
            action=ActionType.DELETE,
            entity_type=entity_type,
            entity_id=entity_id,
            actor_id=actor_id,
            before=before,
            after=None,
            ip_address=ip_address,
            user_agent=user_agent,
        )
    
    async def log_export(
        self,
        entity_type: str,
        actor_id: Optional[UUID],
        filters: Optional[dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> AuditLog:
        """Записать экспорт"""
        return await self.log_action(
            action=ActionType.EXPORT,
            entity_type=entity_type,
            entity_id=UUID("00000000-0000-0000-0000-000000000000"),  # Нет конкретной сущности
            actor_id=actor_id,
            before=None,
            after={"filters": filters} if filters else None,
            ip_address=ip_address,
            user_agent=user_agent,
        )

