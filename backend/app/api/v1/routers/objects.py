"""
Роутер объектов
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.objects import ObjectCreate, ObjectUpdate, ObjectOut
from app.api.v1.schemas.pagination import PageParams, PageResponse
from app.api.v1.deps.security import get_current_user, require_scopes
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, Object, ObjectStatus
from app.infrastructure.db.repositories.object_repository import ObjectRepository
from app.core.pagination import get_pagination_offset
from app.core.logging_config import get_logger
from app.domain.services.audit_service import AuditService
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=PageResponse[ObjectOut])
async def list_objects(
    city_id: Optional[UUID] = Query(None),
    district_id: Optional[UUID] = Query(None),
    status: Optional[ObjectStatus] = Query(None),
    search: Optional[str] = Query(None),
    params: PageParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список объектов с фильтрацией и пагинацией"""
    logger.info(
        "List objects requested",
        user_id=str(current_user.id),
        user_role=current_user.role.value,
        filters={
            "city_id": str(city_id) if city_id else None,
            "district_id": str(district_id) if district_id else None,
            "status": status.value if status else None,
            "search": search,
            "page": params.page,
            "limit": params.limit,
        }
    )
    
    repo = ObjectRepository(db)
    offset = get_pagination_offset(params.page, params.limit)
    
    items, total = await repo.find_by_filters(
        city_id=city_id,
        district_id=district_id,
        status=status,
        search_query=search,
        limit=params.limit,
        offset=offset,
    )
    
    pages = (total + params.limit - 1) // params.limit
    
    logger.debug(
        "List objects completed",
        user_id=str(current_user.id),
        total=total,
        returned=len(items),
        pages=pages,
    )
    
    return PageResponse(
        items=[ObjectOut.model_validate(item) for item in items],
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )


@router.post("/", response_model=ObjectOut, status_code=201)
async def create_object(
    data: ObjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать объект"""
    logger.info(
        "Creating object",
        user_id=str(current_user.id),
        user_name=current_user.full_name,
        object_type=data.type.value,
        address=data.address,
        city_id=str(data.city_id),
    )
    
    repo = ObjectRepository(db)
    
    new_object = Object(
        type=data.type,
        address=data.address,
        city_id=data.city_id,
        district_id=data.district_id,
        gps_lat=data.gps_lat,
        gps_lng=data.gps_lng,
        status=data.status,
        tags=data.tags,
        responsible_user_id=data.responsible_user_id,
        contact_name=data.contact_name,
        contact_phone=data.contact_phone,
        created_by=current_user.id,
    )
    
    obj = await repo.add(new_object)
    await db.commit()
    
    # Логируем в аудит
    try:
        audit_service = AuditService(db)
        after_data = {
            "id": str(obj.id),
            "type": obj.type.value,
            "address": obj.address,
            "status": obj.status.value,
        }
        await audit_service.log_create(
            entity_type="object",
            entity_id=obj.id,
            actor_id=current_user.id,
            after=after_data,
        )
        await db.commit()
        logger.debug("Audit log created for object creation", object_id=str(obj.id))
    except Exception as e:
        logger.error("Failed to create audit log", error=str(e), object_id=str(obj.id))
    
    logger.info(
        "Object created successfully",
        object_id=str(obj.id),
        user_id=str(current_user.id),
    )
    
    return ObjectOut.model_validate(obj)


@router.get("/{object_id}", response_model=ObjectOut)
async def get_object(
    object_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить объект по ID"""
    logger.debug(
        "Getting object",
        object_id=str(object_id),
        user_id=str(current_user.id),
    )
    
    repo = ObjectRepository(db)
    obj = await repo.get(object_id)
    
    if not obj:
        logger.warning(
            "Object not found",
            object_id=str(object_id),
            user_id=str(current_user.id),
        )
        from app.core.errors import NotFoundError
        raise NotFoundError("Object", object_id)
    
    logger.debug(
        "Object retrieved",
        object_id=str(object_id),
        status=obj.status.value,
        user_id=str(current_user.id),
    )
    
    return ObjectOut.model_validate(obj)


@router.patch("/{object_id}", response_model=ObjectOut)
async def update_object(
    object_id: UUID,
    data: ObjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить объект"""
    logger.info(
        "Updating object",
        object_id=str(object_id),
        user_id=str(current_user.id),
        user_name=current_user.full_name,
        update_fields=list(data.model_dump(exclude_unset=True, exclude={"version"}).keys()),
    )
    
    repo = ObjectRepository(db)
    obj = await repo.get(object_id)
    
    if not obj:
        logger.warning(
            "Object not found for update",
            object_id=str(object_id),
            user_id=str(current_user.id),
        )
        from app.core.errors import NotFoundError
        raise NotFoundError("Object", object_id)
    
    # Сохраняем старое состояние для аудита
    before_data = {
        "id": str(obj.id),
        "status": obj.status.value,
        "type": obj.type.value,
        "address": obj.address,
        "responsible_user_id": str(obj.responsible_user_id) if obj.responsible_user_id else None,
    }
    
    # Optimistic locking (проверяет версию, используя индекс version)
    if data.version is not None and obj.version != data.version:
        logger.warning(
            "Version conflict on object update",
            object_id=str(object_id),
            expected_version=data.version,
            current_version=obj.version,
            user_id=str(current_user.id),
        )
        from app.core.errors import ConflictError
        raise ConflictError(
            "Object was modified by another user",
            diff={
                "expected_version": data.version,
                "current_version": obj.version,
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
        old_value = getattr(obj, key, None)
        setattr(obj, key, value)
        logger.debug(
            "Object field updated",
            object_id=str(object_id),
            field=key,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(value) if value is not None else None,
        )
    
    obj.updated_by = current_user.id
    obj.version += 1
    
    obj = await repo.update(obj)
    await db.commit()
    
    # Логируем в аудит
    try:
        audit_service = AuditService(db)
        after_data = {
            "id": str(obj.id),
            "status": obj.status.value,
            "type": obj.type.value,
            "address": obj.address,
            "responsible_user_id": str(obj.responsible_user_id) if obj.responsible_user_id else None,
        }
        await audit_service.log_update(
            entity_type="object",
            entity_id=obj.id,
            actor_id=current_user.id,
            before=before_data,
            after=after_data,
        )
        await db.commit()
        logger.debug("Audit log created for object update", object_id=str(obj.id))
    except Exception as e:
        logger.error("Failed to create audit log", error=str(e), object_id=str(obj.id))
    
    logger.info(
        "Object updated successfully",
        object_id=str(object_id),
        user_id=str(current_user.id),
        new_version=obj.version,
    )
    
    return ObjectOut.model_validate(obj)
