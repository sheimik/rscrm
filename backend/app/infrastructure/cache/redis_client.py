"""
Redis клиент для кэша и очередей
"""
import redis.asyncio as redis
from typing import Optional

from app.core.config import settings


_redis_client: Optional[redis.Redis] = None


async def get_redis_client() -> redis.Redis:
    """Получить Redis клиент (singleton)"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis_client():
    """Закрыть Redis клиент"""
    global _redis_client
    if _redis_client:
        await _redis_client.aclose()
        _redis_client = None

