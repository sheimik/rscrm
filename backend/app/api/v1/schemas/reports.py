"""
Pydantic схемы для отчётов
"""
from uuid import UUID
from typing import Optional, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime


class ReportCreate(BaseModel):
    """Создание задачи экспорта"""
    entity: Literal["objects", "visits", "customers"] = Field(
        ..., 
        description="Тип сущности",
        examples=["objects"]
    )
    filters: Optional[dict[str, Any]] = Field(
        None, 
        description="Фильтры",
        examples=[{"status": "NEW", "city_id": "..."}]
    )
    columns: Optional[list[str]] = Field(
        None, 
        description="Колонки для экспорта",
        examples=[["id", "address", "status", "visits_count"]]
    )
    sort: Optional[dict[str, Any]] = Field(
        None, 
        description="Сортировка",
        examples=[{"updated_at": "desc"}]
    )


class ReportJobOut(BaseModel):
    """Вывод задачи экспорта"""
    id: UUID
    owner_id: UUID
    entity: str
    filters_json: Optional[dict[str, Any]] = None
    columns: Optional[list[str]] = None
    sort: Optional[dict[str, Any]] = None
    status: str
    file_path: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class ReportPreviewRequest(BaseModel):
    """Запрос превью отчёта"""
    entity: Literal["objects", "visits", "customers"]
    filters: Optional[dict[str, Any]] = None
    columns: Optional[list[str]] = None
    sort: Optional[dict[str, Any]] = None
    limit: int = Field(default=100, ge=1, le=1000)


class ReportPreviewResponse(BaseModel):
    """Ответ превью"""
    rows: list[dict[str, Any]]
    total: int
    columns: list[str]

