"""
Скрипт для создания города и районов
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.infrastructure.db.models import City, District
from app.core.config import settings
from sqlalchemy import select


async def create_city(city_name: str, districts: list[str] = None):
    """Создать город и районы"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем, существует ли уже такой город
        result = await session.execute(select(City).where(City.name == city_name))
        existing_city = result.scalar_one_or_none()
        
        if existing_city:
            print(f"[SKIP] Город '{city_name}' уже существует (ID: {existing_city.id})")
            return existing_city.id
        
        # Создаем город
        city = City(name=city_name)
        session.add(city)
        await session.flush()
        
        print(f"[OK] Город '{city_name}' создан (ID: {city.id})")
        
        # Создаем районы, если указаны
        if districts:
            district_objects = []
            for district_name in districts:
                district = District(name=district_name, city_id=city.id)
                district_objects.append(district)
            
            session.add_all(district_objects)
            print(f"[OK] Создано районов: {len(districts)}")
            for i, district_name in enumerate(districts, 1):
                print(f"   {i}. {district_name}")
        
        await session.commit()
        
        print(f"\n[SUCCESS] Город '{city_name}' успешно создан!")
        return city.id
    
    await engine.dispose()


async def main():
    """Главная функция"""
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  python {sys.argv[0]} <название_города> [район1] [район2] ...")
        print("\nПримеры:")
        print(f"  python {sys.argv[0]} Новосибирск")
        print(f"  python {sys.argv[0]} Екатеринбург Центральный Ленинский Чкаловский")
        sys.exit(1)
    
    city_name = sys.argv[1]
    districts = sys.argv[2:] if len(sys.argv) > 2 else None
    
    await create_city(city_name, districts)


if __name__ == "__main__":
    asyncio.run(main())

