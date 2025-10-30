"""
Роутер офлайн-синхронизации
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from datetime import datetime

from app.api.v1.schemas.sync import (
    SyncBatchRequest,
    SyncBatchResponse,
    SyncItemResult,
    SyncChangesRequest,
    SyncChangesResponse,
    SyncChangeItem,
)
from app.api.v1.deps.security import get_current_user
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User
from app.domain.services.sync_service import SyncService
from app.core.errors import ConflictError
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


@router.post("/batch", response_model=SyncBatchResponse)
async def sync_batch(
    request: SyncBatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Batch-синхронизация (идемпотентная)
    
    Принимает пачку upsert'ов с client_generated_id.
    Возвращает результаты синхронизации, включая конфликты.
    """
    service = SyncService(db)
    
    results = []
    conflicts_count = 0
    errors_count = 0
    
    for item in request.items:
        try:
            server_id, status, diff = await service.upsert_item(
                client_id=item.client_generated_id,
                table_name=item.table_name,
                payload=item.payload,
                version=item.version,
                force=request.force,
            )
            
            result = SyncItemResult(
                client_generated_id=item.client_generated_id,
                server_id=server_id,
                status=status,
                server_version=item.version,
            )
            results.append(result)
            
            if status == "conflict":
                conflicts_count += 1
                result.diff = diff
            
        except ConflictError as e:
            conflicts_count += 1
            error_details = e.details.get("diff", {})
            
            # Получаем server_id из существующего токена
            from app.infrastructure.db.repositories.sync_repository import SyncRepository
            sync_repo = SyncRepository(db)
            existing_token = await sync_repo.get_by_client_id(item.client_generated_id)
            server_id = existing_token.server_id if existing_token else UUID("00000000-0000-0000-0000-000000000000")
            
            result = SyncItemResult(
                client_generated_id=item.client_generated_id,
                server_id=server_id,
                status="conflict",
                diff=error_details,
                server_version=error_details.get("current_version"),
                resolution_hints=error_details.get("resolution_hints"),
            )
            results.append(result)
            
        except Exception as e:
            errors_count += 1
            result = SyncItemResult(
                client_generated_id=item.client_generated_id,
                server_id=UUID("00000000-0000-0000-0000-000000000000"),
                status="error",
                error_message=str(e),
            )
            results.append(result)
    
    await db.commit()
    
    return SyncBatchResponse(
        results=results,
        conflicts_count=conflicts_count,
        errors_count=errors_count,
    )


@router.get("/changes", response_model=SyncChangesResponse)
async def sync_changes(
    since: datetime = Query(..., description="ISO дата последней синхронизации"),
    tables: str = Query(..., description="Список таблиц через запятую"),
    limit: int = Query(default=1000, ge=1, le=10000),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Получить изменения с сервера
    
    Возвращает дельту изменений с указанной даты.
    """
    table_list = [t.strip() for t in tables.split(",")]
    
    service = SyncService(db)
    changes = await service.get_changes(
        tables=table_list,
        since=since,
        limit=limit,
    )
    
    items = [
        SyncChangeItem(
            id=change["id"],
            table_name=change["table_name"],
            action=change["action"],
            data=change["data"],
            updated_at=change["updated_at"],
            version=change["version"],
        )
        for change in changes
    ]
    
    has_more = len(changes) >= limit
    
    return SyncChangesResponse(
        items=items,
        has_more=has_more,
        next_cursor=str(changes[-1]["updated_at"]) if has_more else None,
    )


@router.post("/changes", response_model=SyncChangesResponse)
async def sync_changes_post(
    request: SyncChangesRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить изменения (POST метод с телом запроса)"""
    service = SyncService(db)
    changes = await service.get_changes(
        tables=request.tables,
        since=request.since,
        limit=request.limit,
    )
    
    items = [
        SyncChangeItem(
            id=change["id"],
            table_name=change["table_name"],
            action=change["action"],
            data=change["data"],
            updated_at=change["updated_at"],
            version=change["version"],
        )
        for change in changes
    ]
    
    has_more = len(changes) >= request.limit
    
    return SyncChangesResponse(
        items=items,
        has_more=has_more,
        next_cursor=str(changes[-1]["updated_at"]) if has_more else None,
    )

