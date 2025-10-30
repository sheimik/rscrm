"""
Зависимости для безопасности и RBAC
"""
from uuid import UUID
from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.core.config import settings
from app.core.security import get_token_payload, get_scopes_from_role
from app.core.errors import UnauthorizedError, ForbiddenError
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_PREFIX}/auth/token")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    """Получить текущего пользователя из JWT"""
    payload = get_token_payload(token)
    user_id = payload.get("sub")
    
    if not user_id:
        raise UnauthorizedError("Invalid token")
    
    try:
        user_uuid = UUID(user_id)
    except ValueError:
        raise UnauthorizedError("Invalid user ID")
    
    result = await db.execute(select(User).where(User.id == user_uuid))
    user = result.scalar_one_or_none()
    
    if not user or not user.is_active:
        raise UnauthorizedError("User not found or inactive")
    
    return user


def require_roles(*roles: UserRole):
    """Декоратор для проверки ролей"""
    def _check_roles(user: User = Depends(get_current_user)) -> User:
        if user.role not in roles:
            raise ForbiddenError(f"Required roles: {', '.join(r.value for r in roles)}")
        return user
    return _check_roles


def require_scopes(*scopes: str):
    """Декоратор для проверки scopes"""
    def _check_scopes(user: User = Depends(get_current_user)) -> User:
        user_scopes = get_scopes_from_role(user.role.value)
        
        # Admin имеет все права
        if "admin:*" in user_scopes:
            return user
        
        for scope in scopes:
            if scope not in user_scopes:
                raise ForbiddenError(f"Missing required scope: {scope}")
        
        return user
    return _check_scopes

