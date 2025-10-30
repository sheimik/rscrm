"""
Унифицированные утилиты для фильтров, пагинации и сортировки
"""
from typing import Optional, Any, Dict
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field


class FilterParams(BaseModel):
    """Базовые параметры фильтрации"""
    q: Optional[str] = Field(None, description="Поиск по тексту")
    page: int = Field(default=1, ge=1, description="Номер страницы")
    limit: int = Field(default=20, ge=1, le=100, description="Количество элементов")
    sort: Optional[str] = Field(None, description="Сортировка: -updated_at,+city или updated_at")


class ObjectFilterParams(FilterParams):
    """Фильтры для объектов"""
    city_id: Optional[UUID] = None
    district_id: Optional[UUID] = None
    status: Optional[str] = None
    type: Optional[str] = None
    responsible_user_id: Optional[UUID] = None


class VisitFilterParams(FilterParams):
    """Фильтры для визитов"""
    engineer_id: Optional[UUID] = None
    object_id: Optional[UUID] = None
    status: Optional[str] = None
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None


class CustomerFilterParams(FilterParams):
    """Фильтры для клиентов"""
    object_id: Optional[UUID] = None
    phone: Optional[str] = None
    interests: Optional[list[str]] = None
    rating_min: Optional[int] = Field(None, ge=1, le=5)
    rating_max: Optional[int] = Field(None, ge=1, le=5)


def parse_sort(sort_str: Optional[str]) -> Dict[str, str]:
    """
    Парсинг строки сортировки: "-updated_at,+city" -> {"updated_at": "desc", "city": "asc"}
    """
    if not sort_str:
        return {}
    
    result = {}
    for field in sort_str.split(","):
        field = field.strip()
        if not field:
            continue
        
        if field.startswith("-"):
            result[field[1:]] = "desc"
        elif field.startswith("+"):
            result[field[1:]] = "asc"
        else:
            result[field] = "asc"
    
    return result

