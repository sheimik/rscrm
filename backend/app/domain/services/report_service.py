"""
Сервис для генерации отчётов
"""
from uuid import UUID, uuid4
from typing import Optional, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.models import ReportJob, Object, Visit, Customer
from app.infrastructure.db.repositories.object_repository import ObjectRepository
from sqlalchemy import select


class ReportService:
    """Сервис отчётов"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create_export_job(
        self,
        owner_id: UUID,
        entity: str,
        filters: Optional[dict[str, Any]] = None,
        columns: Optional[list[str]] = None,
        sort: Optional[dict[str, Any]] = None,
    ) -> ReportJob:
        """Создать задачу экспорта"""
        job = ReportJob(
            id=uuid4(),
            owner_id=owner_id,
            entity=entity,
            filters_json=filters,
            columns=columns,
            sort=sort,
            status="pending",
        )
        
        self.session.add(job)
        await self.session.flush()
        
        return job
    
    async def preview_report(
        self,
        entity: str,
        filters: Optional[dict[str, Any]] = None,
        columns: Optional[list[str]] = None,
        sort: Optional[dict[str, Any]] = None,
        limit: int = 100,
    ) -> dict[str, Any]:
        """Предпросмотр отчёта"""
        # Получаем данные
        if entity == "objects":
            data = await self._get_objects_preview(filters, sort, limit)
        elif entity == "visits":
            data = await self._get_visits_preview(filters, sort, limit)
        elif entity == "customers":
            data = await self._get_customers_preview(filters, sort, limit)
        else:
            data = {"rows": [], "total": 0, "columns": []}
        
        # Фильтруем колонки, если указаны
        if columns and data["rows"]:
            filtered_rows = []
            for row in data["rows"]:
                filtered_row = {k: v for k, v in row.items() if k in columns}
                filtered_rows.append(filtered_row)
            data["rows"] = filtered_rows
            data["columns"] = columns
        
        return data
    
    async def _get_objects_preview(
        self,
        filters: Optional[dict[str, Any]],
        sort: Optional[dict[str, Any]],
        limit: int,
    ) -> dict[str, Any]:
        """Получить превью объектов"""
        stmt = select(Object).limit(limit)
        
        if filters:
            # Применяем фильтры (упрощённо)
            pass
        
        result = await self.session.execute(stmt)
        objects = list(result.scalars().all())
        
        rows = []
        for obj in objects:
            rows.append({
                "id": str(obj.id),
                "type": obj.type.value if hasattr(obj.type, "value") else str(obj.type),
                "address": obj.address,
                "city": obj.city.name if obj.city else "",
                "district": obj.district.name if obj.district else "",
                "status": obj.status.value if hasattr(obj.status, "value") else str(obj.status),
                "visits_count": obj.visits_count,
                "last_visit_at": obj.last_visit_at.isoformat() if obj.last_visit_at else None,
            })
        
        return {
            "rows": rows,
            "total": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        }
    
    async def _get_visits_preview(
        self,
        filters: Optional[dict[str, Any]],
        sort: Optional[dict[str, Any]],
        limit: int,
    ) -> dict[str, Any]:
        """Получить превью визитов"""
        stmt = select(Visit).limit(limit)
        
        result = await self.session.execute(stmt)
        visits = list(result.scalars().all())
        
        rows = []
        for visit in visits:
            rows.append({
                "id": str(visit.id),
                "object_id": str(visit.object_id),
                "engineer_id": str(visit.engineer_id),
                "status": visit.status.value if hasattr(visit.status, "value") else str(visit.status),
                "scheduled_at": visit.scheduled_at.isoformat() if visit.scheduled_at else None,
                "finished_at": visit.finished_at.isoformat() if visit.finished_at else None,
            })
        
        return {
            "rows": rows,
            "total": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        }
    
    async def _get_customers_preview(
        self,
        filters: Optional[dict[str, Any]],
        sort: Optional[dict[str, Any]],
        limit: int,
    ) -> dict[str, Any]:
        """Получить превью клиентов"""
        stmt = select(Customer).limit(limit)
        
        result = await self.session.execute(stmt)
        customers = list(result.scalars().all())
        
        rows = []
        for customer in customers:
            rows.append({
                "id": str(customer.id),
                "object_id": str(customer.object_id),
                "full_name": customer.full_name,
                "phone": customer.phone,
                "interests": customer.interests or [],
            })
        
        return {
            "rows": rows,
            "total": len(rows),
            "columns": list(rows[0].keys()) if rows else [],
        }

