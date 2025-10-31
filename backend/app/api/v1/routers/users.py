"""
Роутер пользователей
"""
from uuid import UUID
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.v1.schemas.users import UserCreate, UserUpdate, UserOut, UserMe
from app.api.v1.deps.security import get_current_user, require_roles
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, UserRole
from app.infrastructure.db.repositories.user_repository import UserRepository
from app.core.security import get_password_hash
from app.core.logging_config import get_logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

router = APIRouter()
logger = get_logger(__name__)


@router.get("/me", response_model=UserMe)
async def get_me(current_user: User = Depends(get_current_user)):
    """Получить текущего пользователя"""
    return UserMe.model_validate(current_user)


@router.get("/", response_model=List[UserOut])
async def list_users(
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Список пользователей (только для админов)"""
    repo = UserRepository(db)
    users = await repo.find()
    return [UserOut.model_validate(u) for u in users]


@router.get("/supervisors", response_model=List[UserOut])
async def search_supervisors(
    q: Optional[str] = Query(None, description="Поиск по имени или email"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Поиск супервайзеров для делегирования"""
    logger.info(
        "Searching supervisors",
        user_id=str(current_user.id),
        search_query=q,
    )
    
    stmt = select(User).where(User.role == UserRole.SUPERVISOR)
    
    if q:
        search_pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                User.full_name.ilike(search_pattern),
                User.email.ilike(search_pattern),
            )
        )
    
    result = await db.execute(stmt)
    supervisors = list(result.scalars().all())
    
    logger.debug(
        "Supervisors found",
        user_id=str(current_user.id),
        count=len(supervisors),
    )
    
    return [UserOut.model_validate(s) for s in supervisors]


@router.post("/", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(
    data: UserCreate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Создать пользователя (только для админов)"""
    repo = UserRepository(db)
    
    # Проверяем, что email уникален
    existing = await repo.get_by_email(data.email)
    if existing:
        from app.core.errors import ValidationError
        raise ValidationError(f"User with email {data.email} already exists")
    
    # Создаём пользователя
    new_user = User(
        email=data.email,
        hashed_password=get_password_hash(data.password),
        full_name=data.full_name,
        phone=data.phone,
        role=data.role,
        city_id=data.city_id,
        district_id=data.district_id,
        is_active=data.is_active,
    )
    
    user = await repo.add(new_user)
    await db.commit()
    
    return UserOut.model_validate(user)


@router.get("/{user_id}", response_model=UserOut)
async def get_user(
    user_id: UUID,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Получить пользователя по ID"""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        from app.core.errors import NotFoundError
        raise NotFoundError("User", user_id)
    
    return UserOut.model_validate(user)


@router.patch("/{user_id}", response_model=UserOut)
async def update_user(
    user_id: UUID,
    data: UserUpdate,
    current_user: User = Depends(require_roles(UserRole.ADMIN)),
    db: AsyncSession = Depends(get_db),
):
    """Обновить пользователя"""
    repo = UserRepository(db)
    user = await repo.get(user_id)
    
    if not user:
        from app.core.errors import NotFoundError
        raise NotFoundError("User", user_id)
    
    # Обновляем поля
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(user, key, value)
    
    user = await repo.update(user)
    await db.commit()
    
    return UserOut.model_validate(user)

