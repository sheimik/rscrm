"""
API v1 роутер
"""
from fastapi import APIRouter

from app.api.v1.routers import (
    auth,
    users,
    objects,
    customers,
    visits,
    dictionaries,
    sync,
    audit,
    reports,
    analytics,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(objects.router, prefix="/objects", tags=["objects"])
api_router.include_router(customers.router, prefix="/customers", tags=["customers"])
api_router.include_router(visits.router, prefix="/visits", tags=["visits"])
api_router.include_router(dictionaries.router, prefix="/dictionaries", tags=["dictionaries"])
api_router.include_router(sync.router, prefix="/sync", tags=["sync"])
api_router.include_router(audit.router, prefix="/audit", tags=["audit"])
api_router.include_router(reports.router, prefix="/reports", tags=["reports"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])

