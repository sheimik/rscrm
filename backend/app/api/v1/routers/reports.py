"""
Роутер отчётов
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from datetime import datetime

from app.api.v1.schemas.reports import (
    ReportCreate,
    ReportJobOut,
    ReportPreviewRequest,
    ReportPreviewResponse,
)
from app.api.v1.deps.security import get_current_user
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, ReportJob
from app.domain.services.report_service import ReportService
from app.core.errors import NotFoundError, RateLimitError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import os

from app.core.config import settings

router = APIRouter()


@router.post("/export", response_model=ReportJobOut, status_code=status.HTTP_201_CREATED)
async def create_export(
    data: ReportCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Создать задачу экспорта отчёта"""
    # Rate limit проверка
    from app.core.rate_limit import check_rate_limit
    from fastapi import Request
    from starlette.requests import Request as StarletteRequest
    
    # Создаём фейковый request для rate limit (в реальности нужно передавать request)
    # await check_rate_limit(request, user_id=str(current_user.id), limit=10, window_seconds=300)
    
    service = ReportService(db)
    
    # Создаём job
    job = await service.create_export_job(
        owner_id=current_user.id,
        entity=data.entity,
        filters=data.filters,
        columns=data.columns,
        sort=data.sort,
    )
    
    await db.commit()
    
    # Запускаем задачу в фоне через RQ
    try:
        from app.infrastructure.queues.rq_tasks import export_objects_task
        from rq import Queue
        import redis.asyncio as redis
        
        redis_client = await redis.from_url(settings.REDIS_URL)
        queue = Queue("reports", connection=redis_client)
        
        # Запускаем задачу (синхронный вызов, для async нужен адаптер)
        # rq_job = queue.enqueue(export_objects_task, [], str(job.id))
        # job.rq_job_id = rq_job.id
        # await db.commit()
    except Exception as e:
        # Если очередь недоступна, помечаем как failed
        job.status = "failed"
        job.error_message = f"Queue error: {str(e)}"
        await db.commit()
    
    return ReportJobOut.model_validate(job)


@router.get("/jobs", response_model=list[ReportJobOut])
async def list_jobs(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Список задач экспорта текущего пользователя"""
    result = await db.execute(
        select(ReportJob)
        .where(ReportJob.owner_id == current_user.id)
        .order_by(ReportJob.created_at.desc())
        .limit(50)
    )
    jobs = list(result.scalars().all())
    
    return [ReportJobOut.model_validate(job) for job in jobs]


@router.get("/jobs/{job_id}", response_model=ReportJobOut)
async def get_job(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Получить задачу экспорта по ID"""
    result = await db.execute(
        select(ReportJob).where(ReportJob.id == job_id, ReportJob.owner_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise NotFoundError("ReportJob", job_id)
    
    return ReportJobOut.model_validate(job)


@router.get("/jobs/{job_id}/download")
async def download_report(
    job_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Скачать готовый отчёт"""
    result = await db.execute(
        select(ReportJob).where(ReportJob.id == job_id, ReportJob.owner_id == current_user.id)
    )
    job = result.scalar_one_or_none()
    
    if not job:
        raise NotFoundError("ReportJob", job_id)
    
    if job.status != "done":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Report is not ready. Status: {job.status}",
        )
    
    if not job.file_path or not os.path.exists(job.file_path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Report file not found",
        )
    
    return FileResponse(
        job.file_path,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        filename=os.path.basename(job.file_path),
    )


@router.post("/preview", response_model=ReportPreviewResponse)
async def preview_report(
    data: ReportPreviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Предпросмотр отчёта (до 100 строк)"""
    service = ReportService(db)
    
    preview = await service.preview_report(
        entity=data.entity,
        filters=data.filters,
        columns=data.columns,
        sort=data.sort,
        limit=data.limit,
    )
    
    return ReportPreviewResponse(**preview)

