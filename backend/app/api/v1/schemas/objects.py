"""
Pydantic схемы для объектов
"""
from uuid import UUID
from typing import Optional, Literal
from pydantic import BaseModel, Field
from datetime import datetime

from app.infrastructure.db.models import ObjectType, ObjectStatus


class ObjectBase(BaseModel):
    """Базовая схема объекта"""
    type: ObjectType
    address: str = Field(..., min_length=5, max_length=500)
    city_id: UUID
    district_id: Optional[UUID] = None
    gps_lat: Optional[float] = Field(None, ge=-90, le=90)
    gps_lng: Optional[float] = Field(None, ge=-180, le=180)
    status: ObjectStatus = ObjectStatus.NEW
    tags: list[str] = Field(default_factory=list)
    responsible_user_id: Optional[UUID] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=32)


class ObjectCreate(ObjectBase):
    """Создание объекта"""
    pass


class ObjectUpdate(BaseModel):
    """Обновление объекта"""
    type: Optional[ObjectType] = None
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    city_id: Optional[UUID] = None
    district_id: Optional[UUID] = None
    gps_lat: Optional[float] = Field(None, ge=-90, le=90)
    gps_lng: Optional[float] = Field(None, ge=-180, le=180)
    status: Optional[ObjectStatus] = None
    tags: Optional[list[str]] = None
    responsible_user_id: Optional[UUID] = None
    contact_name: Optional[str] = Field(None, max_length=255)
    contact_phone: Optional[str] = Field(None, max_length=32)
    version: Optional[int] = None  # Для optimistic locking


class ObjectOut(ObjectBase):
    """Вывод объекта"""
    id: UUID
    visits_count: int
    last_visit_at: Optional[datetime] = None
    created_by: UUID
    updated_by: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    version: int
    
    class Config:
        from_attributes = True
