"""
Pydantic схемы для клиентов
"""
from uuid import UUID
from typing import Optional, Literal
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime

from app.api.v1.schemas.common import PIIFieldsMixin, mask_phone


class CustomerBase(BaseModel):
    """Базовая схема клиента"""
    object_id: UUID
    unit_id: Optional[UUID] = None
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    portrait_text: Optional[str] = None
    current_provider: Optional[str] = Field(None, max_length=255)
    provider_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfied: Optional[bool] = None
    interests: list[str] = Field(default_factory=list)
    preferred_call_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    desired_price: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None
    gdpr_consent: bool = False


class CustomerCreate(CustomerBase):
    """Создание клиента"""
    pass


class CustomerUpdate(BaseModel):
    """Обновление клиента"""
    full_name: Optional[str] = Field(None, max_length=255)
    phone: Optional[str] = Field(None, max_length=20)
    portrait_text: Optional[str] = None
    current_provider: Optional[str] = Field(None, max_length=255)
    provider_rating: Optional[int] = Field(None, ge=1, le=5)
    satisfied: Optional[bool] = None
    interests: Optional[list[str]] = None
    preferred_call_time: Optional[str] = Field(None, pattern=r'^\d{2}:\d{2}$')
    desired_price: Optional[str] = Field(None, max_length=50)
    notes: Optional[str] = None


class CustomerOut(CustomerBase, PIIFieldsMixin):
    """Вывод клиента
    
    Примечание: Поле `phone` маскируется для пользователей без доступа к PII (ENGINEER).
    ADMIN и SUPERVISOR видят полные данные.
    """
    id: UUID = Field(..., examples=["123e4567-e89b-12d3-a456-426614174000"])
    last_interaction_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    
    @field_serializer("phone")
    def serialize_phone(self, phone: Optional[str], info) -> Optional[str]:
        """Маскирование телефона (применяется через mask_pii)"""
        return phone  # Реальное маскирование в mask_pii
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "examples": [{
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "object_id": "...",
                "full_name": "Иван Иванов",
                "phone": "+7 (***) ***-**89",  # Маскировано для ENGINEER
                "interests": ["INTERNET", "TV"],
                "provider_rating": 4,
                "created_at": "2025-01-15T10:00:00Z",
                "updated_at": "2025-01-15T10:00:00Z",
            }]
        }

