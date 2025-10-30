"""
Репозиторий для клиентов
"""
from uuid import UUID
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models import Customer


class CustomerRepository(BaseRepository[Customer]):
    """Репозиторий клиентов"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, Customer)
    
    async def get_by_phone(self, phone: str) -> Optional[Customer]:
        """Получить клиента по телефону (использует UNIQUE индекс)"""
        result = await self.session.execute(
            select(Customer).where(Customer.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def find_by_object(
        self,
        object_id: UUID,
        limit: int = 100,
        offset: int = 0,
    ) -> tuple[list[Customer], int]:
        """Найти клиентов по объекту (использует индекс object_id)"""
        stmt = select(Customer).where(Customer.object_id == object_id)
        count_stmt = select(func.count()).select_from(Customer).where(Customer.object_id == object_id)
        
        # Получаем общее количество
        total_result = await self.session.execute(count_stmt)
        total = total_result.scalar_one()
        
        # Применяем пагинацию (использует индекс updated_at для сортировки)
        stmt = stmt.order_by(Customer.updated_at.desc()).limit(limit).offset(offset)
        
        result = await self.session.execute(stmt)
        items = list(result.scalars().all())
        
        return items, total

