"""
Роутер аналитики
"""
from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, Query
from datetime import datetime, timedelta

from app.api.v1.deps.security import get_current_user
from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import User, Object, Visit
from app.infrastructure.db.repositories.object_repository import ObjectRepository
from app.infrastructure.db.repositories.visit_repository import VisitRepository
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

router = APIRouter()


@router.get("/summary")
async def get_summary(
    period: str = Query(default="month", description="Период: day, week, month, year"),
    city_id: Optional[UUID] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Сводная аналитика (использует индексы для быстрых запросов)"""
    # Вычисляем период
    now = datetime.utcnow()
    period_map = {
        "day": timedelta(days=1),
        "week": timedelta(weeks=1),
        "month": timedelta(days=30),
        "year": timedelta(days=365),
    }
    since = now - period_map.get(period, timedelta(days=30))
    
    obj_repo = ObjectRepository(db)
    visit_repo = VisitRepository(db)
    
    # Объекты в работе (использует индекс status)
    objects_in_work, _ = await obj_repo.find_by_filters(
        status="INTEREST" if hasattr(Object, "INTEREST") else None,
        city_id=city_id,
        limit=1000,
        offset=0,
    )
    
    # Визиты за период (использует индекс scheduled_at)
    visits, _ = await visit_repo.find_by_filters(
        date_from=since,
        date_to=now,
        limit=1000,
        offset=0,
    )
    
    completed_visits = [v for v in visits if v.status == "DONE"]
    
    return {
        "period": period,
        "since": since.isoformat(),
        "objects_in_work": len(objects_in_work),
        "total_visits": len(visits),
        "completed_visits": len(completed_visits),
        "completion_rate": len(completed_visits) / len(visits) if visits else 0,
    }


@router.get("/objects/by-city")
async def get_objects_by_city(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Распределение объектов по городам (использует индекс city_id)"""
    stmt = select(
        Object.city_id,
        func.count(Object.id).label("count"),
        func.count(Object.id).filter(Object.status == "INTEREST").label("in_work"),
    ).group_by(Object.city_id)
    
    result = await db.execute(stmt)
    rows = result.all()
    
    return {
        "items": [
            {
                "city_id": str(row.city_id),
                "total": row.count,
                "in_work": row.in_work,
            }
            for row in rows
        ]
    }

