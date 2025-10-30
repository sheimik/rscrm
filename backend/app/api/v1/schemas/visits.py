"""
Pydantic схемы для визитов
"""
from uuid import UUID
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from app.infrastructure.db.models import VisitStatus, InterestType


class VisitBase(BaseModel):
    """Базовая схема визита"""
    object_id: UUID
    unit_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    interests: list[str] = Field(default_factory=list)  # InterestType enum values


class VisitCreate(VisitBase):
    """Создание визита"""
    pass


class VisitUpdate(BaseModel):
    """Обновление визита"""
    object_id: Optional[UUID] = None
    unit_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    scheduled_at: Optional[datetime] = None
    status: Optional[VisitStatus] = None
    interests: Optional[list[str]] = None
    outcome_text: Optional[str] = None
    next_action_due_at: Optional[datetime] = None
    geo_captured_lat: Optional[float] = Field(None, ge=-90, le=90)
    geo_captured_lng: Optional[float] = Field(None, ge=-180, le=180)
    version: Optional[int] = None  # Для optimistic locking


class VisitComplete(BaseModel):
    """Завершение визита"""
    status: Literal["DONE", "CANCELLED"] = "DONE"
    outcome_text: str = Field(..., min_length=1)
    interests: list[str] = Field(default_factory=list)
    next_action_due_at: Optional[datetime] = None
    geo_captured_lat: Optional[float] = Field(None, ge=-90, le=90)
    geo_captured_lng: Optional[float] = Field(None, ge=-180, le=180)
    version: int = Field(..., ge=1)


class VisitOut(VisitBase):
    """Вывод визита"""
    id: UUID
    engineer_id: UUID
    status: VisitStatus
    started_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    outcome_text: Optional[str] = None
    next_action_due_at: Optional[datetime] = None
    geo_captured_lat: Optional[float] = None
    geo_captured_lng: Optional[float] = None
    version: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

