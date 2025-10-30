"""
Сервис офлайн-синхронизации
"""
from uuid import UUID, uuid4
from datetime import datetime
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.errors import ConflictError, ValidationError
from app.infrastructure.db.models import Object, Visit, Customer
from app.infrastructure.db.repositories.sync_repository import SyncRepository


class SyncService:
    """Сервис синхронизации"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.sync_repo = SyncRepository(session)
    
    async def upsert_item(
        self,
        client_id: UUID,
        table_name: str,
        payload: dict[str, Any],
        version: Optional[int] = None,
        force: bool = False,
    ) -> tuple[UUID, str, Optional[dict]]:
        """
        Upsert элемента синхронизации
        
        Returns:
            (server_id, status, diff) - server_id, статус операции, diff при конфликте
        """
        # Проверяем существующий токен
        existing_token = await self.sync_repo.get_by_client_id(client_id)
        
        if existing_token:
            # Обновление существующей записи
            server_id = existing_token.server_id
            entity = await self.sync_repo.get_entity_by_table(table_name, server_id)
            
            if not entity:
                # Запись была удалена, создаём новую
                return await self._create_entity(table_name, payload, client_id)
            
            # Проверяем версию для optimistic locking
            if hasattr(entity, "version") and version is not None:
                if entity.version != version and not force:
                    # Конфликт версий
                    diff = await self._calculate_diff(entity, payload)
                    server_data = await self._entity_to_dict(entity)
                    
                    raise ConflictError(
                        f"Version conflict for {table_name}",
                        diff={
                            "expected_version": version,
                            "current_version": entity.version,
                            "server_data": server_data,
                            "client_data": payload,
                            "diff": diff,
                            "resolution_hints": {
                                "code": "STALE_VERSION",
                                "strategy": "merge|force|reject",
                                "message": "Server version is newer. Use force=true to overwrite or apply merge on client.",
                            },
                        }
                    )
            
            # Обновляем сущность
            await self._update_entity(entity, payload)
            entity.version = (entity.version if hasattr(entity, "version") else 1) + 1
            await self.session.flush()
            
            return server_id, "updated", None
        else:
            # Создание новой записи
            return await self._create_entity(table_name, payload, client_id)
    
    async def _create_entity(
        self,
        table_name: str,
        payload: dict[str, Any],
        client_id: UUID,
    ) -> tuple[UUID, str, None]:
        """Создать новую сущность"""
        server_id = uuid4()
        
        if table_name == "objects":
            entity = Object(id=server_id, **payload)
        elif table_name == "visits":
            entity = Visit(id=server_id, **payload)
        elif table_name == "customers":
            entity = Customer(id=server_id, **payload)
        else:
            raise ValidationError(f"Unknown table: {table_name}")
        
        self.session.add(entity)
        await self.session.flush()
        
        # Создаём токен синхронизации
        await self.sync_repo.upsert_token(client_id, table_name, server_id)
        
        return server_id, "created", None
    
    async def _update_entity(self, entity: Any, payload: dict[str, Any]) -> None:
        """Обновить сущность из payload"""
        for key, value in payload.items():
            if hasattr(entity, key) and not key.startswith("_"):
                setattr(entity, key, value)
    
    async def _entity_to_dict(self, entity: Any) -> dict[str, Any]:
        """Конвертировать сущность в словарь"""
        result = {}
        for column in entity.__table__.columns:
            value = getattr(entity, column.name)
            if isinstance(value, datetime):
                result[column.name] = value.isoformat()
            elif isinstance(value, UUID):
                result[column.name] = str(value)
            else:
                result[column.name] = value
        return result
    
    async def _calculate_diff(self, server_entity: Any, client_payload: dict[str, Any]) -> dict[str, Any]:
        """Вычислить разницу между серверной и клиентской версиями"""
        server_dict = await self._entity_to_dict(server_entity)
        diff = {}
        
        for key, client_value in client_payload.items():
            server_value = server_dict.get(key)
            if server_value != client_value:
                diff[key] = {
                    "server": server_value,
                    "client": client_value,
                }
        
        # Поля, которые есть только на сервере
        for key in server_dict:
            if key not in client_payload:
                diff[key] = {
                    "server": server_dict[key],
                    "client": None,
                }
        
        return diff
    
    async def get_changes(
        self,
        tables: list[str],
        since: datetime,
        limit: int = 1000,
    ) -> list[dict[str, Any]]:
        """Получить изменения с указанной даты"""
        all_changes = []
        
        for table_name in tables:
            entities = await self.sync_repo.find_changes_since(table_name, since, limit)
            
            for entity in entities:
                change_item = {
                    "id": entity.id,
                    "table_name": table_name,
                    "action": "update",  # Упрощённо, можно добавить логику для delete
                    "data": await self._entity_to_dict(entity),
                    "updated_at": entity.updated_at if hasattr(entity, "updated_at") else datetime.utcnow(),
                    "version": entity.version if hasattr(entity, "version") else 1,
                }
                all_changes.append(change_item)
        
        # Сортируем по updated_at
        all_changes.sort(key=lambda x: x["updated_at"])
        
        return all_changes[:limit]

