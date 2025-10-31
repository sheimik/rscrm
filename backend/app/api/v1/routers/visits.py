"""
Роутер визитов
"""
from uuid import UUID
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.visits import VisitCreate, VisitUpdate, VisitComplete, VisitOut
from app.api.v1.schemas.pagination import PageParams, PageResponse
from app.api.v1.deps.security import get_current_user
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, Visit, VisitStatus
from app.infrastructure.db.repositories.visit_repository import VisitRepository
from app.core.pagination import get_pagination_offset
from app.core.errors import NotFoundError, ConflictError
from app.core.logging_config import get_logger
from app.domain.services.audit_service import AuditService
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=PageResponse[VisitOut])
async def list_visits(
    object_id: Optional[UUID] = Query(None),
    engineer_id: Optional[UUID] = Query(None),
    customer_id: Optional[UUID] = Query(None),
    status: Optional[VisitStatus] = Query(None),
    date_from: Optional[datetime] = Query(None),
    date_to: Optional[datetime] = Query(None),
    params: PageParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список визитов с фильтрацией и пагинацией"""
    
    repo = VisitRepository(db)
    offset = get_pagination_offset(params.page, params.limit)
    
    # Если ENGINEER, показываем только его визиты
    if current_user.role.value == "ENGINEER":
        engineer_id = current_user.id
    
    items, total = await repo.find_by_filters(
        object_id=object_id,
        engineer_id=engineer_id,
        customer_id=customer_id,
        status=status,
        date_from=date_from,
        date_to=date_to,
        limit=params.limit,
        offset=offset,
    )
    
    pages = (total + params.limit - 1) // params.limit if total > 0 else 0
    
    return PageResponse(
        items=[VisitOut.model_validate(item) for item in items],
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )


@router.post("/", response_model=VisitOut, status_code=201)
async def create_visit(
    data: VisitCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать визит"""
    logger.info(
        "Creating visit",
        user_id=str(current_user.id),
        user_name=current_user.full_name,
        object_id=str(data.object_id),
        scheduled_at=str(data.scheduled_at) if data.scheduled_at else None,
    )
    
    from app.infrastructure.db.models import Visit as VisitModel
    
    # ENGINEER может создавать визиты только для себя
    # Примечание: в VisitCreate нет поля engineer_id, оно всегда берется из текущего пользователя
    engineer_id = current_user.id
    
    new_visit = VisitModel(
        object_id=data.object_id,
        unit_id=data.unit_id,
        customer_id=data.customer_id,
        scheduled_at=data.scheduled_at,
        engineer_id=engineer_id,
        status=VisitStatus.PLANNED,
        interests=data.interests or [],
    )
    
    db.add(new_visit)
    await db.commit()
    await db.refresh(new_visit)
    
    # Логируем в аудит
    try:
        audit_service = AuditService(db)
        after_data = {
            "id": str(new_visit.id),
            "object_id": str(new_visit.object_id),
            "status": new_visit.status.value,
            "engineer_id": str(new_visit.engineer_id),
        }
        await audit_service.log_create(
            entity_type="visit",
            entity_id=new_visit.id,
            actor_id=current_user.id,
            after=after_data,
        )
        await db.commit()
        logger.debug("Audit log created for visit creation", visit_id=str(new_visit.id))
    except Exception as e:
        logger.error("Failed to create audit log", error=str(e), visit_id=str(new_visit.id))
    
    logger.info(
        "Visit created successfully",
        visit_id=str(new_visit.id),
        user_id=str(current_user.id),
    )
    
    return VisitOut.model_validate(new_visit)


@router.get("/{visit_id}", response_model=VisitOut)
async def get_visit(
    visit_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить визит по ID"""
    
    repo = VisitRepository(db)
    visit = await repo.get(visit_id)
    
    if not visit:
        raise NotFoundError("Visit", visit_id)
    
    # ENGINEER может видеть только свои визиты
    if current_user.role.value == "ENGINEER" and visit.engineer_id != current_user.id:
        raise NotFoundError("Visit", visit_id)
    
    return VisitOut.model_validate(visit)


@router.patch("/{visit_id}", response_model=VisitOut)
async def update_visit(
    visit_id: UUID,
    data: VisitUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить визит"""
    
    repo = VisitRepository(db)
    visit = await repo.get(visit_id)
    
    if not visit:
        raise NotFoundError("Visit", visit_id)
    
    # ENGINEER может обновлять только свои визиты
    if current_user.role.value == "ENGINEER" and visit.engineer_id != current_user.id:
        raise NotFoundError("Visit", visit_id)
    
    # Optimistic locking
    if data.version is not None and visit.version != data.version:
        raise ConflictError(
            "Visit was modified by another user",
            diff={
                "expected_version": data.version,
                "current_version": visit.version,
                "resolution_hints": {
                    "code": "STALE_VERSION",
                    "strategy": "merge|force|reject",
                    "message": "Server version is newer. Use force=true to overwrite or apply merge on client.",
                }
            }
        )
    
    # Обновляем поля
    update_data = data.model_dump(exclude_unset=True, exclude={"version"})
    for key, value in update_data.items():
        setattr(visit, key, value)
    
    visit.version += 1
    
    visit = await repo.update(visit)
    await db.commit()
    
    return VisitOut.model_validate(visit)


@router.post("/{visit_id}/complete", response_model=VisitOut)
async def complete_visit(
    visit_id: UUID,
    data: VisitComplete,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Завершить визит"""
    
    repo = VisitRepository(db)
    visit = await repo.get(visit_id)
    
    if not visit:
        raise NotFoundError("Visit", visit_id)
    
    # ENGINEER может завершать только свои визиты
    if current_user.role.value == "ENGINEER" and visit.engineer_id != current_user.id:
        raise NotFoundError("Visit", visit_id)
    
    # Optimistic locking
    if visit.version != data.version:
        raise ConflictError(
            "Visit was modified by another user",
            diff={
                "expected_version": data.version,
                "current_version": visit.version,
                "resolution_hints": {
                    "code": "STALE_VERSION",
                    "strategy": "merge|force|reject",
                    "message": "Server version is newer. Use force=true to overwrite or apply merge on client.",
                }
            }
        )
    
    # Обновляем визит
    visit.status = VisitStatus.DONE if data.status == "DONE" else VisitStatus.CANCELLED
    visit.outcome_text = data.outcome_text
    visit.interests = data.interests or []
    visit.next_action_due_at = data.next_action_due_at
    visit.geo_captured_lat = data.geo_captured_lat
    visit.geo_captured_lng = data.geo_captured_lng
    visit.finished_at = datetime.utcnow()
    
    if not visit.started_at:
        visit.started_at = datetime.utcnow()
    
    visit.version += 1
    
    visit = await repo.update(visit)
    await db.commit()
    
    # Обновляем счетчики объекта
    from app.infrastructure.db.repositories.object_repository import ObjectRepository
    obj_repo = ObjectRepository(db)
    obj = await obj_repo.get(visit.object_id)
    if obj:
        obj.visits_count = (obj.visits_count or 0) + 1
        obj.last_visit_at = visit.finished_at
        await obj_repo.update(obj)
        await db.commit()
    
    return VisitOut.model_validate(visit)

