"""
Роутер авторизации
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from app.api.v1.schemas.auth import TokenRequest, TokenResponse, RefreshTokenRequest
from app.core.config import settings
from app.core.security import (
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    get_scopes_from_role,
)
from app.core.errors import UnauthorizedError
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, UserRole
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

router = APIRouter()


@router.post("/token", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """OAuth2 Password Flow - получение JWT токенов"""
    # Получаем пользователя по email (username в OAuth2)
    result = await db.execute(select(User).where(User.email == form_data.username))
    user = result.scalar_one_or_none()
    
    if not user:
        raise UnauthorizedError("Invalid email or password")
    
    if not user.is_active:
        raise UnauthorizedError("User is inactive")
    
    # Проверяем пароль
    if not verify_password(form_data.password, user.hashed_password):
        raise UnauthorizedError("Invalid email or password")
    
    # Обновляем last_login_at
    from datetime import datetime
    user.last_login_at = datetime.utcnow()
    await db.commit()
    
    # Получаем scopes для роли
    scopes = get_scopes_from_role(user.role.value)
    
    # Создаём токены
    access_token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "scopes": scopes,
        },
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    
    refresh_token = create_refresh_token(
        data={
            "sub": str(user.id),
            "email": user.email,
        }
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """Обновление access token через refresh token"""
    try:
        payload = decode_token(request.refresh_token)
        
        if payload.get("type") != "refresh":
            raise UnauthorizedError("Invalid token type")
        
        user_id = payload.get("sub")
        if not user_id:
            raise UnauthorizedError("Invalid token")
        
        # Получаем пользователя
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active:
            raise UnauthorizedError("User not found or inactive")
        
        # Создаём новый access token
        scopes = get_scopes_from_role(user.role.value)
        access_token = create_access_token(
            data={
                "sub": str(user.id),
                "email": user.email,
                "role": user.role.value,
                "scopes": scopes,
            },
            expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
        )
        
        # Новый refresh token (опционально, можно оставить старый)
        refresh_token = create_refresh_token(
            data={
                "sub": str(user.id),
                "email": user.email,
            }
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
    
    except Exception as e:
        raise UnauthorizedError("Invalid refresh token")


@router.post("/logout")
async def logout():
    """Выход (заглушка, при JWT обычно не нужен, можно добавить blacklist)"""
    return {"message": "Logged out successfully"}

