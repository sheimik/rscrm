"""
Pydantic схемы для аудита
"""
from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime

from app.infrastructure.db.models import ActionType


class AuditLogOut(BaseModel):
    """Вывод записи аудита"""
    id: UUID
    actor_id: Optional[UUID] = None
    action: ActionType
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    before_json: Optional[dict[str, Any]] = None
    after_json: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    occurred_at: datetime
    
    class Config:
        from_attributes = True


class AuditFilterParams(BaseModel):
    """Параметры фильтрации аудита"""
    actor_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[ActionType] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None

