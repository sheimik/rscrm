"""
Скрипт создания администратора.
Запускается так:
    python scripts/create_admin.py <email> <password> [full_name]
"""
import asyncio
import sys
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Делаем backend корнем Python-пути и гарантируем правильную точку отчёта
BACKEND_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BACKEND_ROOT))

# Импорты проекта идут после настройки пути
from app.core.config import settings  # type: ignore  # pylint: disable=wrong-import-position
from app.core.security import get_password_hash  # type: ignore  # pylint: disable=wrong-import-position
from app.infrastructure.db.base import Base  # type: ignore  # pylint: disable=wrong-import-position
from app.infrastructure.db.models import User, UserRole  # type: ignore  # pylint: disable=wrong-import-position


async def ensure_schema(engine) -> None:
    """Гарантируем, что БД существует и таблицы созданы."""
    data_dir = BACKEND_ROOT / "data"
    data_dir.mkdir(exist_ok=True)
    (data_dir / "files").mkdir(exist_ok=True)
    (data_dir / "reports").mkdir(exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def create_admin(email: str, password: str, full_name: str) -> None:
    """Создать администратора."""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    Session = async_sessionmaker(engine, expire_on_commit=False)

    await ensure_schema(engine)

    try:
        async with Session() as session:
            result = await session.execute(select(User).where(User.email == email))
            existing = result.scalar_one_or_none()

            if existing:
                print(f"User with email {email} already exists. Nothing to do.")
                return

            admin = User(
                email=email,
                hashed_password=get_password_hash(password),
                full_name=full_name,
                role=UserRole.ADMIN,
                is_active=True,
            )

            session.add(admin)
            await session.commit()

            print("Admin user created successfully:")
            print(f"  Email: {email}")
            print(f"  Name:  {full_name}")
            print(f"  Role:  {admin.role.value}")
    finally:
        await engine.dispose()


def main(argv: list[str]) -> None:
    if len(argv) < 3:
        print("Usage: python scripts/create_admin.py <email> <password> [full_name]")
        sys.exit(1)

    email = argv[1]
    password = argv[2]
    full_name = argv[3] if len(argv) > 3 else "Admin"

    asyncio.run(create_admin(email, password, full_name))


if __name__ == "__main__":
    main(sys.argv)
