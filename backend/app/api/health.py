"""
Health и readiness пробы
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from typing import Optional

from app.infrastructure.db.base import get_db
from app.infrastructure.cache.redis_client import get_redis_client
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def health_check():
    """Базовая проверка работоспособности API"""
    return {"status": "ok", "service": "api"}


@router.get("/ready")
async def readiness_check(
    db: AsyncSession = Depends(get_db),
):
    """Проверка готовности: БД доступна"""
    try:
        # Проверка подключения к БД
        result = await db.execute(text("SELECT 1"))
        result.scalar_one()
        
        return {
            "status": "ready",
            "service": "api",
            "database": "connected",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Database unavailable: {str(e)}")


@router.get("/metrics")
async def metrics(
    db: AsyncSession = Depends(get_db),
):
    """Метрики для мониторинга"""
    try:
        # Подключение к Redis (опционально)
        redis_available = False
        queue_length = None
        try:
            redis = await get_redis_client()
            if redis:
                redis_available = True
                # Длина очереди RQ (при наличии)
                try:
                    from redis import Redis
                    r = Redis.from_url(settings.REDIS_URL)
                    queue_length = r.llen("rq:queue:default")
                except:
                    pass
        except:
            pass
        
        # Базовые метрики БД
        db_ok = False
        try:
            result = await db.execute(text("SELECT 1"))
            result.scalar_one()
            db_ok = True
        except:
            pass
        
        return {
            "status": "ok",
            "database": "connected" if db_ok else "disconnected",
            "redis": "connected" if redis_available else "disconnected",
            "queue_length": queue_length,
            "rate_limit_enabled": settings.RATE_LIMIT_ENABLED,
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
        }


@router.get("/worker/health")
async def worker_health():
    """Проверка работоспособности worker (RQ)"""
    try:
        from redis import Redis
        r = Redis.from_url(settings.REDIS_URL)
        
        # Проверка подключения к Redis
        r.ping()
        
        # Длина очереди
        queue_length = r.llen("rq:queue:default")
        
        # Количество воркеров
        workers = r.smembers("rq:workers")
        worker_count = len(workers)
        
        return {
            "status": "ok",
            "service": "worker",
            "redis": "connected",
            "queue_length": queue_length,
            "workers": worker_count,
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "worker",
            "error": str(e),
        }


@router.get("/worker/ready")
async def worker_readiness():
    """Проверка готовности worker: Redis доступен"""
    try:
        from redis import Redis
        r = Redis.from_url(settings.REDIS_URL)
        r.ping()
        
        return {
            "status": "ready",
            "service": "worker",
            "redis": "connected",
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unavailable: {str(e)}")

