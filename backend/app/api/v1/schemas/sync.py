"""
Pydantic схемы для офлайн-синхронизации
"""
from uuid import UUID
from typing import Optional, Literal, Any
from pydantic import BaseModel, Field
from datetime import datetime


class SyncItem(BaseModel):
    """Элемент синхронизации"""
    client_generated_id: UUID = Field(
        ..., 
        description="UUID сгенерированный клиентом",
        examples=["550e8400-e29b-41d4-a716-446655440000"]
    )
    table_name: str = Field(
        ..., 
        description="Имя таблицы (objects, visits, customers)",
        examples=["objects"]
    )
    payload: dict[str, Any] = Field(
        ..., 
        description="Данные сущности",
        examples=[{"address": "ул. Новая, д. 1", "city_id": "...", "status": "NEW"}]
    )
    updated_at: datetime = Field(
        ..., 
        description="Время последнего изменения на клиенте",
        examples=["2025-01-15T10:00:00Z"]
    )
    version: Optional[int] = Field(None, ge=1, description="Версия для optimistic locking", examples=[5])


class SyncBatchRequest(BaseModel):
    """Запрос batch-синхронизации"""
    items: list[SyncItem] = Field(..., min_items=1, max_items=1000, description="Список элементов для синхронизации")
    force: bool = Field(
        default=False, 
        description="Принудительное разрешение конфликтов (последняя версия побеждает)",
        examples=[False]
    )


class SyncItemResult(BaseModel):
    """Результат синхронизации одного элемента"""
    client_generated_id: UUID
    server_id: UUID
    status: Literal["created", "updated", "conflict", "error"]
    error_message: Optional[str] = None
    diff: Optional[dict[str, Any]] = None  # Для конфликтов
    server_version: Optional[int] = None
    resolution_hints: Optional[dict[str, Any]] = None  # Подсказки для разрешения конфликтов


class SyncBatchResponse(BaseModel):
    """Ответ batch-синхронизации"""
    results: list[SyncItemResult]
    conflicts_count: int = 0
    errors_count: int = 0


class SyncChangesRequest(BaseModel):
    """Запрос изменений с сервера"""
    since: datetime = Field(..., description="ISO дата последней синхронизации")
    tables: list[str] = Field(..., description="Список таблиц для получения изменений")
    limit: int = Field(default=1000, ge=1, le=10000)


class SyncChangeItem(BaseModel):
    """Элемент изменения с сервера"""
    id: UUID
    table_name: str
    action: Literal["create", "update", "delete"]
    data: Optional[dict[str, Any]] = None
    updated_at: datetime
    version: int


class SyncChangesResponse(BaseModel):
    """Ответ изменений"""
    items: list[SyncChangeItem]
    has_more: bool
    next_cursor: Optional[str] = None

