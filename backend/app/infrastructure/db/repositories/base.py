"""
Базовый репозиторий
"""
from typing import Generic, TypeVar, Optional, Any
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

T = TypeVar("T")


class BaseRepository(Generic[T]):
    """Базовый репозиторий с CRUD операциями"""
    
    def __init__(self, session: AsyncSession, model: type[T]):
        self.session = session
        self.model = model
    
    async def get(self, id: UUID) -> Optional[T]:
        """Получить по ID"""
        result = await self.session.execute(
            select(self.model).where(self.model.id == id)
        )
        return result.scalar_one_or_none()
    
    async def find_one(self, **filters: Any) -> Optional[T]:
        """Найти один по фильтрам"""
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()
    
    async def find(self, **filters: Any) -> list[T]:
        """Найти все по фильтрам"""
        stmt = select(self.model)
        for key, value in filters.items():
            stmt = stmt.where(getattr(self.model, key) == value)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())
    
    async def add(self, entity: T) -> T:
        """Добавить сущность"""
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def update(self, entity: T) -> T:
        """Обновить сущность"""
        await self.session.flush()
        await self.session.refresh(entity)
        return entity
    
    async def delete(self, entity: T) -> None:
        """Удалить сущность"""
        await self.session.delete(entity)
        await self.session.flush()
    
    async def upsert_by_client_id(
        self,
        client_id: UUID,
        table_name: str,
        entity_data: dict[str, Any],
    ) -> T:
        """Upsert по client_generated_id (для офлайн-синхры)"""
        # Эта логика зависит от конкретной таблицы, переопределяется в наследниках
        raise NotImplementedError

