"""
Роутер аудита
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from datetime import datetime

from app.api.v1.schemas.audit import AuditLogOut, AuditFilterParams
from app.api.v1.schemas.pagination import PageParams, PageResponse
from app.api.v1.deps.security import get_current_user, require_roles
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, UserRole, AuditLog, ActionType
from app.core.pagination import get_pagination_offset
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func


router = APIRouter()


@router.get("/", response_model=PageResponse[AuditLogOut])
async def list_audit_logs(
    actor_id: Optional[UUID] = Query(None),
    entity_type: Optional[str] = Query(None),
    entity_id: Optional[UUID] = Query(None),
    action: Optional[ActionType] = Query(None),
    since: Optional[datetime] = Query(None),
    until: Optional[datetime] = Query(None),
    params: PageParams = Depends(),
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    db: AsyncSession = Depends(get_db),
):
    """Список записей аудита с фильтрацией"""
    stmt = select(AuditLog)
    conditions = []
    
    if actor_id:
        conditions.append(AuditLog.actor_id == actor_id)
    
    if entity_type:
        conditions.append(AuditLog.entity_type == entity_type)
    
    if entity_id:
        conditions.append(AuditLog.entity_id == entity_id)
    
    if action:
        conditions.append(AuditLog.action == action)
    
    if since:
        conditions.append(AuditLog.occurred_at >= since)
    
    if until:
        conditions.append(AuditLog.occurred_at <= until)
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    # Подсчёт общего количества
    count_stmt = select(AuditLog).where(and_(*conditions)) if conditions else select(AuditLog)
    total_result = await db.execute(select(func.count()).select_from(count_stmt.subquery()))
    total = total_result.scalar_one() or 0
    
    # Применяем пагинацию
    offset = get_pagination_offset(params.page, params.limit)
    stmt = stmt.order_by(AuditLog.occurred_at.desc()).limit(params.limit).offset(offset)
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    pages = (total + params.limit - 1) // params.limit if total > 0 else 0
    
    return PageResponse(
        items=[AuditLogOut.model_validate(item) for item in items],
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )


@router.get("/{log_id}", response_model=AuditLogOut)
async def get_audit_log(
    log_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN, UserRole.SUPERVISOR)),
    db: AsyncSession = Depends(get_db),
):
    """Получить запись аудита по ID"""
    result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
    log = result.scalar_one_or_none()
    
    if not log:
        from app.core.errors import NotFoundError
        raise NotFoundError("AuditLog", log_id)
    
    return AuditLogOut.model_validate(log)

