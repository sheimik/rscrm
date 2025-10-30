"""
Unit of Work паттерн
"""
from abc import ABC, abstractmethod
from typing import Protocol
from sqlalchemy.ext.asyncio import AsyncSession

from app.infrastructure.db.repositories.user_repository import UserRepository
from app.infrastructure.db.repositories.object_repository import ObjectRepository
from app.infrastructure.db.repositories.visit_repository import VisitRepository
from app.infrastructure.db.repositories.customer_repository import CustomerRepository


class UnitOfWork(ABC):
    """Абстрактный Unit of Work"""
    
    @abstractmethod
    async def __aenter__(self):
        pass
    
    @abstractmethod
    async def __aexit__(self, *args):
        pass
    
    @abstractmethod
    async def commit(self):
        pass
    
    @abstractmethod
    async def rollback(self):
        pass


class UnitOfWorkImpl(UnitOfWork):
    """Реализация Unit of Work"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
        self.users: UserRepository | None = None
        self.objects: ObjectRepository | None = None
        self.visits: VisitRepository | None = None
        self.customers: CustomerRepository | None = None
    
    async def __aenter__(self):
        self.users = UserRepository(self.session)
        self.objects = ObjectRepository(self.session)
        self.visits = VisitRepository(self.session)
        self.customers = CustomerRepository(self.session)
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.rollback()
        else:
            await self.commit()
    
    async def commit(self):
        await self.session.commit()
    
    async def rollback(self):
        await self.session.rollback()


async def get_uow(session: AsyncSession) -> UnitOfWorkImpl:
    """Dependency для получения UoW"""
    return UnitOfWorkImpl(session)

