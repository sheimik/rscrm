"""
Утилиты для пагинации (page-based и cursor-based)
"""
from typing import Generic, TypeVar, Optional
from pydantic import BaseModel, Field

T = TypeVar("T")


class PageParams(BaseModel):
    """Параметры page-based пагинации"""
    page: int = Field(default=1, ge=1, description="Номер страницы (начиная с 1)")
    limit: int = Field(default=20, ge=1, le=100, description="Количество элементов на странице")


class CursorParams(BaseModel):
    """Параметры cursor-based пагинации"""
    cursor: Optional[str] = Field(default=None, description="Курсор для следующей страницы")
    size: int = Field(default=20, ge=1, le=100, description="Размер страницы")


class PageResponse(BaseModel, Generic[T]):
    """Ответ page-based пагинации"""
    items: list[T]
    page: int
    limit: int
    total: int
    pages: int
    
    @property
    def has_next(self) -> bool:
        return self.page < self.pages
    
    @property
    def has_prev(self) -> bool:
        return self.page > 1


class CursorResponse(BaseModel, Generic[T]):
    """Ответ cursor-based пагинации"""
    items: list[T]
    next_cursor: Optional[str] = None
    has_more: bool


def get_pagination_offset(page: int, limit: int) -> int:
    """Получить offset для SQL запроса"""
    return (page - 1) * limit

