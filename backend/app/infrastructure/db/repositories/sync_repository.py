"""
Репозиторий для синхронизации
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models import SyncToken, Object, Visit, Customer


class SyncRepository(BaseRepository[SyncToken]):
    """Репозиторий для синхронизации"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, SyncToken)
        self.session = session
    
    async def get_by_client_id(self, client_id: UUID) -> Optional[SyncToken]:
        """Получить токен по client_generated_id"""
        result = await self.session.execute(
            select(SyncToken).where(SyncToken.client_generated_id == client_id)
        )
        return result.scalar_one_or_none()
    
    async def upsert_token(
        self,
        client_id: UUID,
        table_name: str,
        server_id: UUID,
        checksum: Optional[str] = None,
    ) -> SyncToken:
        """Создать или обновить токен синхронизации"""
        existing = await self.get_by_client_id(client_id)
        
        if existing:
            existing.server_id = server_id
            existing.checksum = checksum
            existing.last_seen_at = datetime.utcnow()
            existing.status = "synced"
            return existing
        
        new_token = SyncToken(
            client_generated_id=client_id,
            table_name=table_name,
            server_id=server_id,
            checksum=checksum,
            status="synced",
        )
        self.session.add(new_token)
        await self.session.flush()
        return new_token
    
    async def get_entity_by_table(
        self,
        table_name: str,
        entity_id: UUID,
    ) -> Optional[Any]:
        """Получить сущность по имени таблицы и ID"""
        table_map = {
            "objects": Object,
            "visits": Visit,
            "customers": Customer,
        }
        
        model = table_map.get(table_name)
        if not model:
            return None
        
        result = await self.session.execute(
            select(model).where(model.id == entity_id)
        )
        return result.scalar_one_or_none()
    
    async def find_changes_since(
        self,
        table_name: str,
        since: datetime,
        limit: int = 1000,
    ) -> list[Any]:
        """Найти изменения в таблице с указанной даты"""
        table_map = {
            "objects": Object,
            "visits": Visit,
            "customers": Customer,
        }
        
        model = table_map.get(table_name)
        if not model:
            return []
        
        # Для SQLite используем updated_at, для Postgres можно использовать updated_at или аудит
        stmt = select(model).where(model.updated_at >= since).order_by(model.updated_at).limit(limit)
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

