"""
Seed-скрипт для справочников (города и районы)
"""
import asyncio
import sys
from pathlib import Path

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.infrastructure.db.models import City, District, Base
from app.core.config import settings


async def seed_dictionaries():
    """Заполнить справочники тестовыми данными"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем, есть ли уже данные
        from sqlalchemy import select
        result = await session.execute(select(City))
        existing_cities = result.scalars().all()
        
        if existing_cities:
            print("[SKIP] Справочники уже заполнены. Пропускаем.")
            return
        
        # Москва
        moscow = City(id=None, name="Москва")
        session.add(moscow)
        await session.flush()
        
        # Районы Москвы
        moscow_districts = [
            District(name="Центральный", city_id=moscow.id),
            District(name="Северный", city_id=moscow.id),
            District(name="Южный", city_id=moscow.id),
            District(name="Восточный", city_id=moscow.id),
            District(name="Западный", city_id=moscow.id),
        ]
        session.add_all(moscow_districts)
        
        # Санкт-Петербург
        spb = City(id=None, name="Санкт-Петербург")
        session.add(spb)
        await session.flush()
        
        # Районы СПб
        spb_districts = [
            District(name="Центральный", city_id=spb.id),
            District(name="Адмиралтейский", city_id=spb.id),
            District(name="Василеостровский", city_id=spb.id),
            District(name="Выборгский", city_id=spb.id),
            District(name="Калининский", city_id=spb.id),
        ]
        session.add_all(spb_districts)
        
        # Казань
        kazan = City(id=None, name="Казань")
        session.add(kazan)
        await session.flush()
        
        kazan_districts = [
            District(name="Центральный", city_id=kazan.id),
            District(name="Приволжский", city_id=kazan.id),
            District(name="Вахитовский", city_id=kazan.id),
        ]
        session.add_all(kazan_districts)
        
        await session.commit()
        print("[OK] Справочники заполнены:")
        print(f"   - Города: Москва, Санкт-Петербург, Казань")
        print(f"   - Районы: {len(moscow_districts + spb_districts + kazan_districts)} шт.")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_dictionaries())

