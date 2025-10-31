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
    actor_name: Optional[str] = None  # Имя пользователя из relationship
    action: ActionType
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    before_json: Optional[dict[str, Any]] = None
    after_json: Optional[dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    occurred_at: datetime
    
    @classmethod
    def from_orm(cls, obj):
        """Кастомная сериализация для извлечения имени пользователя из relationship"""
        actor_name = None
        if hasattr(obj, 'actor') and obj.actor:
            actor_name = obj.actor.full_name
        
        return cls(
            id=obj.id,
            actor_id=obj.actor_id,
            actor_name=actor_name,
            action=obj.action,
            entity_type=obj.entity_type,
            entity_id=obj.entity_id,
            before_json=obj.before_json,
            after_json=obj.after_json,
            ip_address=obj.ip_address,
            user_agent=obj.user_agent,
            occurred_at=obj.occurred_at,
        )
    
    @classmethod
    def model_validate(cls, obj, **kwargs):
        """Валидация с поддержкой ORM объектов"""
        # Если это ORM объект, используем from_orm
        if hasattr(obj, 'actor'):
            return cls.from_orm(obj)
        # Иначе стандартная валидация
        if isinstance(obj, dict) and 'actor_name' in obj:
            return super().model_validate(obj, **kwargs)
        # Если передан dict без actor_name, но есть actor объект
        if isinstance(obj, dict):
            return super().model_validate(obj, **kwargs)
        # Для ORM объектов
        return cls.from_orm(obj)


class AuditFilterParams(BaseModel):
    """Параметры фильтрации аудита"""
    actor_id: Optional[UUID] = None
    entity_type: Optional[str] = None
    entity_id: Optional[UUID] = None
    action: Optional[ActionType] = None
    since: Optional[datetime] = None
    until: Optional[datetime] = None

