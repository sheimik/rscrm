"""
FastAPI приложение - точка входа
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.core.errors import AppError, app_error_handler
from app.core.logging_config import setup_logging
from app.api.v1 import api_router as api_router_v1
from app.api.health import router as health_router
from app.middlewares.logging import LoggingMiddleware
from app.middlewares.request_id import RequestIDMiddleware
from app.middlewares.audit import AuditMiddleware

# Инициализация логирования
setup_logging(log_level=settings.LOG_LEVEL, log_file="logs/app.log")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Управление жизненным циклом приложения"""
    # Startup
    from app.infrastructure.db.base import engine
    from app.infrastructure.cache.redis_client import get_redis_client
    
    # Проверка подключений (Redis опционален)
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
    except Exception:
        # Redis не доступен - продолжаем без него
        pass
    
    yield
    
    # Shutdown
    await engine.dispose()
    try:
        redis_client = await get_redis_client()
        await redis_client.aclose()
    except Exception:
        pass


app = FastAPI(
    title=settings.APP_NAME,
    version="1.0.0",
    description="CRM Backend API - управление объектами, визитами и клиентами",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middlewares
app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuditMiddleware)  # Аудит после логирования

# Error handlers
app.add_exception_handler(AppError, app_error_handler)
app.add_exception_handler(Exception, lambda req, exc: JSONResponse(
    status_code=500,
    content={"detail": "Internal server error"},
))

# Health checks
app.include_router(health_router)

# API Routes
app.include_router(api_router_v1, prefix=settings.API_V1_PREFIX)


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Подробная проверка здоровья"""
    from app.infrastructure.db.base import engine
    from app.infrastructure.cache.redis_client import get_redis_client
    
    db_status = "ok"
    try:
        async with engine.connect() as conn:
            await conn.execute("SELECT 1")
    except Exception:
        db_status = "error"
    
    redis_status = "ok"
    try:
        redis_client = await get_redis_client()
        await redis_client.ping()
    except Exception:
        redis_status = "error"
    
    return {
        "status": "ok" if db_status == "ok" and redis_status == "ok" else "degraded",
        "database": db_status,
        "redis": redis_status,
    }

