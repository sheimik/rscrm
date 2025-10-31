"""
Роутер клиентов
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query

from app.api.v1.schemas.customers import CustomerOut, CustomerCreate, CustomerUpdate
from app.api.v1.schemas.pagination import PageParams, PageResponse
from app.api.v1.deps.security import get_current_user, require_scopes
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, Customer
from app.core.pagination import get_pagination_offset
from app.core.security import SCOPES
from app.core.phone_normalization import normalize_phone
from app.core.logging_config import get_logger
from app.domain.services.audit_service import AuditService
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.api.v1.schemas.common import mask_phone

router = APIRouter()
logger = get_logger(__name__)


@router.get("/", response_model=PageResponse[CustomerOut])
async def list_customers(
    q: Optional[str] = Query(None, description="Поиск по имени/телефону/адресу"),
    object_id: Optional[UUID] = Query(None),
    phone: Optional[str] = Query(None),
    interests: Optional[str] = Query(None, description="Список интересов через запятую"),
    rating_min: Optional[int] = Query(None, ge=1, le=5),
    rating_max: Optional[int] = Query(None, ge=1, le=5),
    params: PageParams = Depends(),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список клиентов с фильтрацией"""
    # Проверка доступа
    from app.core.security import get_scopes_from_role
    user_scopes = get_scopes_from_role(current_user.role.value)
    has_pii_access = "admin:*" in user_scopes or current_user.role.value == "ADMIN"
    
    stmt = select(Customer)
    conditions = []
    
    if q:
        search_pattern = f"%{q.lower()}%"
        conditions.append(
            or_(
                Customer.full_name.ilike(search_pattern),
                Customer.phone.ilike(search_pattern),
                Customer.portrait_text.ilike(search_pattern),
            )
        )
    
    if object_id:
        conditions.append(Customer.object_id == object_id)
    
    if phone:
        conditions.append(Customer.phone == phone)
    
    if interests:
        interest_list = [i.strip() for i in interests.split(",")]
        # Упрощённо - поиск по JSON массиву (для SQLite работает, для Postgres нужен другой подход)
        for interest in interest_list:
            conditions.append(Customer.interests.contains([interest]))
    
    if rating_min is not None:
        conditions.append(Customer.provider_rating >= rating_min)
    
    if rating_max is not None:
        conditions.append(Customer.provider_rating <= rating_max)
    
    if conditions:
        if len(conditions) == 1:
            stmt = stmt.where(conditions[0])
        else:
            stmt = stmt.where(or_(*conditions))
    
    # Подсчёт общего количества
    count_stmt = select(Customer)
    if conditions:
        if len(conditions) == 1:
            count_stmt = count_stmt.where(conditions[0])
        else:
            count_stmt = count_stmt.where(or_(*conditions))
    
    total_result = await db.execute(select(func.count()).select_from(count_stmt.subquery()))
    total = total_result.scalar_one() or 0
    
    # Применяем пагинацию
    offset = get_pagination_offset(params.page, params.limit)
    stmt = stmt.order_by(Customer.updated_at.desc()).limit(params.limit).offset(offset)
    
    result = await db.execute(stmt)
    items = list(result.scalars().all())
    
    pages = (total + params.limit - 1) // params.limit if total > 0 else 0
    
    # Применяем маскирование PII для пользователей без доступа
    customers_out = []
    for customer in items:
        customer_dict = CustomerOut.model_validate(customer).model_dump()
        if not has_pii_access and customer_dict.get("phone"):
            customer_dict["phone"] = mask_phone(customer_dict["phone"])
        customers_out.append(CustomerOut(**customer_dict))
    
    return PageResponse(
        items=customers_out,
        page=params.page,
        limit=params.limit,
        total=total,
        pages=pages,
    )


@router.post("/", response_model=CustomerOut, status_code=201)
async def create_customer(
    data: CustomerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать клиента"""
    logger.info(
        "Creating customer",
        user_id=str(current_user.id),
        user_name=current_user.full_name,
        object_id=str(data.object_id) if hasattr(data, 'object_id') else None,
    )
    
    customer_data = data.model_dump()
    
    # Нормализуем телефон перед сохранением (для UNIQUE индекса)
    if customer_data.get("phone"):
        customer_data["phone"] = normalize_phone(customer_data["phone"])
    
    new_customer = Customer(**customer_data)
    
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
    # Логируем в аудит
    try:
        audit_service = AuditService(db)
        after_data = {
            "id": str(new_customer.id),
            "object_id": str(new_customer.object_id),
            "phone": "***" if new_customer.phone else None,  # Маскируем PII
        }
        await audit_service.log_create(
            entity_type="customer",
            entity_id=new_customer.id,
            actor_id=current_user.id,
            after=after_data,
        )
        await db.commit()
        logger.debug("Audit log created for customer creation", customer_id=str(new_customer.id))
    except Exception as e:
        logger.error("Failed to create audit log", error=str(e), customer_id=str(new_customer.id))
    
    logger.info(
        "Customer created successfully",
        customer_id=str(new_customer.id),
        user_id=str(current_user.id),
    )
    
    return CustomerOut.model_validate(new_customer)


@router.get("/{customer_id}", response_model=CustomerOut)
async def get_customer(
    customer_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить клиента по ID"""
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    
    if not customer:
        from app.core.errors import NotFoundError
        raise NotFoundError("Customer", customer_id)
    
    # Проверка доступа к PII
    from app.core.security import get_scopes_from_role
    user_scopes = get_scopes_from_role(current_user.role.value)
    has_pii_access = "admin:*" in user_scopes or current_user.role.value == "ADMIN"
    
    customer_out = CustomerOut.model_validate(customer)
    if not has_pii_access:
        customer_out = customer_out.mask_pii(has_access=False)
    
    return customer_out


@router.patch("/{customer_id}", response_model=CustomerOut)
async def update_customer(
    customer_id: UUID,
    data: CustomerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Обновить клиента"""
    logger.info(
        "Updating customer",
        customer_id=str(customer_id),
        user_id=str(current_user.id),
        user_name=current_user.full_name,
    )
    
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    
    if not customer:
        logger.warning(
            "Customer not found for update",
            customer_id=str(customer_id),
            user_id=str(current_user.id),
        )
        from app.core.errors import NotFoundError
        raise NotFoundError("Customer", customer_id)
    
    # Сохраняем старое состояние для аудита
    before_data = {
        "id": str(customer.id),
        "object_id": str(customer.object_id),
    }
    
    # Обновляем поля
    update_data = data.model_dump(exclude_unset=True)
    
    # Нормализуем телефон перед обновлением (для UNIQUE индекса)
    if "phone" in update_data and update_data["phone"]:
        update_data["phone"] = normalize_phone(update_data["phone"])
    
    for key, value in update_data.items():
        old_value = getattr(customer, key, None)
        setattr(customer, key, value)
        logger.debug(
            "Customer field updated",
            customer_id=str(customer_id),
            field=key,
            old_value=str(old_value) if old_value is not None else None,
            new_value=str(value) if value is not None else None,
        )
    
    await db.commit()
    await db.refresh(customer)
    
    # Логируем в аудит
    try:
        audit_service = AuditService(db)
        after_data = {
            "id": str(customer.id),
            "object_id": str(customer.object_id),
        }
        await audit_service.log_update(
            entity_type="customer",
            entity_id=customer.id,
            actor_id=current_user.id,
            before=before_data,
            after=after_data,
        )
        await db.commit()
        logger.debug("Audit log created for customer update", customer_id=str(customer_id))
    except Exception as e:
        logger.error("Failed to create audit log", error=str(e), customer_id=str(customer_id))
    
    logger.info(
        "Customer updated successfully",
        customer_id=str(customer_id),
        user_id=str(current_user.id),
    )
    
    # Проверка доступа к PII
    from app.core.security import get_scopes_from_role
    user_scopes = get_scopes_from_role(current_user.role.value)
    has_pii_access = "admin:*" in user_scopes or current_user.role.value == "ADMIN"
    
    customer_out = CustomerOut.model_validate(customer)
    if not has_pii_access:
        customer_out = customer_out.mask_pii(has_access=False)
    
    return customer_out

