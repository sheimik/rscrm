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
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

router = APIRouter()


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
    
    return ObjectOut.model_validate(obj)


@router.get("/{object_id}", response_model=ObjectOut)
async def get_object(
    object_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить объект по ID"""
    
    repo = ObjectRepository(db)
    obj = await repo.get(object_id)
    
    if not obj:
        from app.core.errors import NotFoundError
        raise NotFoundError("Object", object_id)
    
    return ObjectOut.model_validate(obj)


@router.patch("/{object_id}", response_model=ObjectOut)
async def update_object(
    object_id: UUID,
    data: ObjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить объект"""
    
    repo = ObjectRepository(db)
    obj = await repo.get(object_id)
    
    if not obj:
        from app.core.errors import NotFoundError
        raise NotFoundError("Object", object_id)
    
    # Optimistic locking (проверяет версию, используя индекс version)
    if data.version is not None and obj.version != data.version:
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
        setattr(obj, key, value)
    
    obj.updated_by = current_user.id
    obj.version += 1
    
    obj = await repo.update(obj)
    await db.commit()
    
    return ObjectOut.model_validate(obj)
