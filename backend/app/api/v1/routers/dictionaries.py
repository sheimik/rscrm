"""
Роутер справочников (города, районы и т.д.)
"""
from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from pydantic import BaseModel
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import City, District

router = APIRouter()


class CityOut(BaseModel):
    """Город"""
    id: UUID
    name: str
    
    class Config:
        from_attributes = True


class DistrictOut(BaseModel):
    """Район"""
    id: UUID
    name: str
    city_id: UUID
    
    class Config:
        from_attributes = True


@router.get("/cities", response_model=List[CityOut])
async def list_cities(
    db: AsyncSession = Depends(get_db),
):
    """Список городов"""
    result = await db.execute(select(City).order_by(City.name))
    cities = result.scalars().all()
    return [CityOut.model_validate(city) for city in cities]


@router.get("/districts", response_model=List[DistrictOut])
async def list_districts(
    city_id: Optional[UUID] = Query(None, description="Фильтр по городу"),
    db: AsyncSession = Depends(get_db),
):
    """Список районов (опционально по городу)"""
    stmt = select(District).order_by(District.name)
    if city_id:
        stmt = stmt.where(District.city_id == city_id)
    result = await db.execute(stmt)
    districts = result.scalars().all()
    return [DistrictOut.model_validate(district) for district in districts]

