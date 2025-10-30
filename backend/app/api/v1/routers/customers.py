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
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, func
from app.api.v1.schemas.common import mask_phone

router = APIRouter()


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
    customer_data = data.model_dump()
    
    # Нормализуем телефон перед сохранением (для UNIQUE индекса)
    if customer_data.get("phone"):
        customer_data["phone"] = normalize_phone(customer_data["phone"])
    
    new_customer = Customer(**customer_data)
    
    db.add(new_customer)
    await db.commit()
    await db.refresh(new_customer)
    
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
    result = await db.execute(select(Customer).where(Customer.id == customer_id))
    customer = result.scalar_one_or_none()
    
    if not customer:
        from app.core.errors import NotFoundError
        raise NotFoundError("Customer", customer_id)
    
    # Обновляем поля
    update_data = data.model_dump(exclude_unset=True)
    
    # Нормализуем телефон перед обновлением (для UNIQUE индекса)
    if "phone" in update_data and update_data["phone"]:
        update_data["phone"] = normalize_phone(update_data["phone"])
    
    for key, value in update_data.items():
        setattr(customer, key, value)
    
    await db.commit()
    await db.refresh(customer)
    
    # Проверка доступа к PII
    from app.core.security import get_scopes_from_role
    user_scopes = get_scopes_from_role(current_user.role.value)
    has_pii_access = "admin:*" in user_scopes or current_user.role.value == "ADMIN"
    
    customer_out = CustomerOut.model_validate(customer)
    if not has_pii_access:
        customer_out = customer_out.mask_pii(has_access=False)
    
    return customer_out

