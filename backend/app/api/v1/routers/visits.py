"""
Роутер визитов
"""
from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def list_visits():
    """Список визитов"""
    return {"message": "Not implemented yet"}

