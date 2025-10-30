"""
Dependencies для rate limiting по ролям
"""
from fastapi import Depends, HTTPException, status
from app.api.v1.deps.security import get_current_user
from app.infrastructure.db.models import User
from app.core.rate_limit import rate_limit
from app.core.security import get_scopes_from_role


async def rate_limit_by_role(
    limit_per_minute: int | None = None,
    current_user: User = Depends(get_current_user),
):
    """
    Rate limiting с учётом роли пользователя
    
    Применяется к эндпойнтам через Depends:
    @router.get("/")
    async def list_objects(
        current_user: User = Depends(rate_limit_by_role),
    ):
    """
    user_scopes = get_scopes_from_role(current_user.role.value)
    rate_key = f"rate_limit:{current_user.id}:{current_user.role.value}"
    
    await rate_limit(
        key=rate_key,
        limit=limit_per_minute,
        user_role=current_user.role,
    )


async def rate_limit_heavy_operations(
    current_user: User = Depends(get_current_user),
):
    """Специальный rate limit для тяжёлых операций (экспорт, массовые операции)"""
    # Для тяжёлых операций лимиты строже
    role_limits = {
        "ADMIN": 20,      # 20 запросов в минуту
        "SUPERVISOR": 10, # 10 запросов в минуту
        "ENGINEER": 5,    # 5 запросов в минуту
    }
    
    limit = role_limits.get(current_user.role.value, 5)
    rate_key = f"rate_limit:heavy:{current_user.id}"
    
    await rate_limit(
        key=rate_key,
        limit=limit,
        window=60,
    )

