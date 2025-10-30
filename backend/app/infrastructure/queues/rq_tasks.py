"""
RQ задачи для фоновой обработки
"""
from rq import get_current_job
import asyncio
from uuid import UUID
from datetime import datetime
import os

from app.services.excel_exporter import ExcelExporter
from app.core.config import settings
from app.infrastructure.db.base import AsyncSessionLocal
from app.infrastructure.db.models import ReportJob
from sqlalchemy import select


async def _export_report_async(job_id: UUID):
    """Асинхронная функция экспорта отчёта"""
    async with AsyncSessionLocal() as session:
        # Получаем job
        result = await session.execute(select(ReportJob).where(ReportJob.id == job_id))
        job = result.scalar_one_or_none()
        
        if not job:
            return
        
        try:
            # Обновляем статус
            job.status = "processing"
            await session.commit()
            
            # Генерируем данные (упрощённо)
            from app.domain.services.report_service import ReportService
            service = ReportService(session)
            
            preview = await service.preview_report(
                entity=job.entity,
                filters=job.filters_json,
                columns=job.columns,
                sort=job.sort,
                limit=10000,  # Максимум для экспорта
            )
            
            # Экспортируем в XLSX
            exporter = ExcelExporter()
            filename = f"report_{job.id}_{job.entity}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
            
            # Конвертируем данные для экспорта
            export_data = preview["rows"]
            
            filepath = await exporter.export_objects(export_data, filename)
            
            # Обновляем job
            job.status = "done"
            job.file_path = filepath
            job.completed_at = datetime.utcnow()
            await session.commit()
            
        except Exception as e:
            job.status = "failed"
            job.error_message = str(e)
            await session.commit()
            raise


def export_report_task(job_id: str):
    """Задача экспорта отчёта (синхронная обёртка для RQ)"""
    job_uuid = UUID(job_id)
    
    # Запускаем асинхронную функцию
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(_export_report_async(job_uuid))
        return result
    finally:
        loop.close()

