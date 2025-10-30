"""
Роутер справочников (города, районы и т.д.)
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from uuid import UUID

router = APIRouter()


class CityOut(BaseModel):
    """Город"""
    id: UUID
    name: str


class DistrictOut(BaseModel):
    """Район"""
    id: UUID
    name: str
    city_id: UUID


@router.get("/cities", response_model=List[CityOut])
async def list_cities():
    """Список городов"""
    # TODO: Реализовать получение из БД
    return []


@router.get("/districts", response_model=List[DistrictOut])
async def list_districts(city_id: UUID = None):
    """Список районов (опционально по городу)"""
    # TODO: Реализовать получение из БД
    return []

