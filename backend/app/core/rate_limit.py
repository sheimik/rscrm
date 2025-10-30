"""
Rate limiting через Redis
"""
from typing import Optional
import redis.asyncio as redis
from fastapi import Request

from app.core.config import settings
from app.core.errors import RateLimitError
from app.infrastructure.cache.redis_client import get_redis_client


async def check_rate_limit(
    request: Request,
    user_id: Optional[str] = None,
    limit: int = None,
    window_seconds: int = 60,
) -> None:
    """Проверка лимита запросов"""
    if not settings.RATE_LIMIT_ENABLED:
        return
    
    limit = limit or settings.RATE_LIMIT_PER_MINUTE
    
    # Ключ для rate limit
    if user_id:
        key = f"rl:user:{user_id}:{request.url.path}"
    else:
        # По IP, если нет пользователя
        client_ip = request.client.host if request.client else "unknown"
        key = f"rl:ip:{client_ip}:{request.url.path}"
    
    redis_client = await get_redis_client()
    
    # Token bucket algorithm (упрощённый)
    current = await redis_client.get(key)
    if current and int(current) >= limit:
        raise RateLimitError(f"Rate limit exceeded: {limit} requests per {window_seconds} seconds")
    
    pipe = redis_client.pipeline()
    pipe.incr(key)
    pipe.expire(key, window_seconds)
    await pipe.execute()

