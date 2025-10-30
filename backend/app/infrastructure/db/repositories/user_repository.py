"""
Репозиторий для пользователей
"""
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.infrastructure.db.repositories.base import BaseRepository
from app.infrastructure.db.models import User, UserRole


class UserRepository(BaseRepository[User]):
    """Репозиторий пользователей"""
    
    def __init__(self, session: AsyncSession):
        super().__init__(session, User)
    
    async def get_by_email(self, email: str) -> User | None:
        """Получить пользователя по email"""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    async def get_by_role(self, role: UserRole) -> list[User]:
        """Получить всех пользователей по роли"""
        result = await self.session.execute(
            select(User).where(User.role == role, User.is_active == True)
        )
        return list(result.scalars().all())

