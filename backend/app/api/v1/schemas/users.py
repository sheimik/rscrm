"""
Pydantic схемы для пользователей
"""
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.infrastructure.db.models import UserRole


class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: UserRole
    city_id: Optional[UUID] = None
    district_id: Optional[UUID] = None
    is_active: bool = True


class UserCreate(UserBase):
    """Создание пользователя"""
    password: str = Field(..., min_length=8)


class UserUpdate(BaseModel):
    """Обновление пользователя"""
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    role: Optional[UserRole] = None
    city_id: Optional[UUID] = None
    district_id: Optional[UUID] = None
    is_active: Optional[bool] = None


class UserOut(UserBase):
    """Вывод пользователя"""
    id: UUID
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class UserMe(UserOut):
    """Текущий пользователь (расширенная версия)"""
    scopes: list[str] = []

