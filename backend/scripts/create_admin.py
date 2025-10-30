"""
Скрипт создания администратора
"""
import asyncio
import sys
from pathlib import Path

# Добавляем путь к приложению
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from app.infrastructure.db.models import User, UserRole
from app.core.security import get_password_hash
from app.core.config import settings


async def create_admin(email: str, password: str, full_name: str = "Admin"):
    """Создать администратора"""
    engine = create_async_engine(settings.DATABASE_URL, echo=True)
    Session = async_sessionmaker(engine, expire_on_commit=False)
    
    async with Session() as session:
        from sqlalchemy import select
        
        # Проверяем, существует ли пользователь
        result = await session.execute(select(User).where(User.email == email))
        existing = result.scalar_one_or_none()
        
        if existing:
            print(f"User with email {email} already exists")
            return
        
        # Создаём администратора
        admin = User(
            email=email,
            hashed_password=get_password_hash(password),
            full_name=full_name,
            role=UserRole.ADMIN,
            is_active=True,
        )
        
        session.add(admin)
        await session.commit()
        
        print(f"Admin user created successfully:")
        print(f"  Email: {email}")
        print(f"  Name: {full_name}")
        print(f"  Role: {admin.role.value}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: python create_admin.py <email> <password> [full_name]")
        sys.exit(1)
    
    email = sys.argv[1]
    password = sys.argv[2]
    full_name = sys.argv[3] if len(sys.argv) > 3 else "Admin"
    
    asyncio.run(create_admin(email, password, full_name))

