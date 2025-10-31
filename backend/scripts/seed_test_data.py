"""
Скрипт для заполнения БД тестовыми данными
"""
import asyncio
import sys
from pathlib import Path
from datetime import datetime, timedelta
from uuid import UUID

# Добавляем корневую директорию в путь
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from app.infrastructure.db.models import (
    User, UserRole, City, District, Object, ObjectType, ObjectStatus,
    Customer, Visit, VisitStatus, InterestType
)
from app.core.security import get_password_hash
from app.core.config import settings


async def seed_test_data():
    """Заполнить БД тестовыми данными"""
    engine = create_async_engine(settings.DATABASE_URL, echo=False)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    async with async_session() as session:
        # Проверяем, есть ли уже данные
        from sqlalchemy import select, func
        result = await session.execute(select(func.count(User.id)))
        user_count = result.scalar_one()
        
        if user_count > 0:
            print("[SKIP] Тестовые данные уже существуют. Пропускаем.")
            return
        
        # Получаем города и районы (должны быть заполнены через seed_dictionaries.py)
        result = await session.execute(select(City).where(City.name == "Москва"))
        moscow = result.scalar_one_or_none()
        
        if not moscow:
            print("[ERROR] Сначала запустите seed_dictionaries.py для заполнения справочников")
            return
        
        result = await session.execute(select(District).where(
            District.city_id == moscow.id,
            District.name == "Центральный"
        ))
        central_district = result.scalar_one_or_none()
        
        result = await session.execute(select(District).where(
            District.city_id == moscow.id,
            District.name == "Северный"
        ))
        north_district = result.scalar_one_or_none()
        
        # Создаём пользователей
        admin = User(
            email="admin@example.com",
            hashed_password=get_password_hash("admin123"),
            full_name="Админов Админ Админович",
            role=UserRole.ADMIN,
            city_id=moscow.id,
            is_active=True,
        )
        session.add(admin)
        await session.flush()
        
        supervisor = User(
            email="supervisor@example.com",
            hashed_password=get_password_hash("supervisor123"),
            full_name="Сидоров Сергей Сергеевич",
            role=UserRole.SUPERVISOR,
            city_id=moscow.id,
            district_id=central_district.id if central_district else None,
            is_active=True,
        )
        session.add(supervisor)
        await session.flush()
        
        engineer1 = User(
            email="engineer1@example.com",
            hashed_password=get_password_hash("engineer123"),
            full_name="Иванов Иван Иванович",
            role=UserRole.ENGINEER,
            city_id=moscow.id,
            district_id=central_district.id if central_district else None,
            is_active=True,
        )
        session.add(engineer1)
        await session.flush()
        
        engineer2 = User(
            email="engineer2@example.com",
            hashed_password=get_password_hash("engineer123"),
            full_name="Петров Пётр Петрович",
            role=UserRole.ENGINEER,
            city_id=moscow.id,
            district_id=north_district.id if north_district else None,
            is_active=True,
        )
        session.add(engineer2)
        await session.flush()
        
        # Создаём объекты
        obj1 = Object(
            type=ObjectType.MKD,
            address="ул. Пушкина, д. 12",
            city_id=moscow.id,
            district_id=central_district.id if central_district else None,
            gps_lat=55.7558,
            gps_lng=37.6173,
            status=ObjectStatus.INTEREST,
            responsible_user_id=engineer1.id,
            created_by=admin.id,
            visits_count=2,
            last_visit_at=datetime.utcnow() - timedelta(days=1),
        )
        session.add(obj1)
        await session.flush()
        
        obj2 = Object(
            type=ObjectType.BUSINESS_CENTER,
            address="пр-т Ленина, д. 50",
            city_id=moscow.id,
            district_id=north_district.id if north_district else None,
            gps_lat=55.7658,
            gps_lng=37.6273,
            status=ObjectStatus.NEW,
            responsible_user_id=engineer2.id,
            created_by=admin.id,
            visits_count=0,
        )
        session.add(obj2)
        await session.flush()
        
        obj3 = Object(
            type=ObjectType.SHOPPING_CENTER,
            address='Торговый комплекс "Галерея"',
            city_id=moscow.id,
            district_id=central_district.id if central_district else None,
            gps_lat=55.7458,
            gps_lng=37.6073,
            status=ObjectStatus.DONE,
            responsible_user_id=supervisor.id,
            created_by=admin.id,
            visits_count=5,
            last_visit_at=datetime.utcnow() - timedelta(days=3),
        )
        session.add(obj3)
        await session.flush()
        
        # Создаём клиентов
        customer1 = Customer(
            object_id=obj1.id,
            full_name="Алексей Смирнов",
            phone="+79123456789",
            portrait_text="Квартира 45",
            current_provider="Конкурент А",
            provider_rating=3,
            interests=[InterestType.INTERNET.value, InterestType.TV.value],
            preferred_call_time="18:00",
            desired_price="800 руб/мес",
            gdpr_consent=True,
        )
        session.add(customer1)
        await session.flush()
        
        customer2 = Customer(
            object_id=obj1.id,
            full_name="Мария Петрова",
            phone="+79051234567",
            portrait_text="Квартира 12",
            current_provider="Конкурент Б",
            provider_rating=2,
            interests=[InterestType.CCTV.value],
            preferred_call_time="14:00",
            desired_price="500 руб/мес",
            gdpr_consent=True,
        )
        session.add(customer2)
        await session.flush()
        
        customer3 = Customer(
            object_id=obj3.id,
            full_name="Иван Козлов",
            phone="+79167890123",
            portrait_text="Офис 301",
            provider_rating=5,
            interests=[InterestType.INTERNET.value, InterestType.TV.value, InterestType.BABY_MONITOR.value],
            desired_price="1200 руб/мес",
            gdpr_consent=True,
        )
        session.add(customer3)
        await session.flush()
        
        # Создаём визиты
        visit1 = Visit(
            object_id=obj1.id,
            customer_id=customer1.id,
            engineer_id=engineer1.id,
            scheduled_at=datetime.utcnow() - timedelta(days=1, hours=2),
            started_at=datetime.utcnow() - timedelta(days=1, hours=2),
            finished_at=datetime.utcnow() - timedelta(days=1),
            status=VisitStatus.DONE,
            interests=[InterestType.INTERNET.value, InterestType.TV.value],
            outcome_text="Клиент заинтересован в подключении",
            next_action_due_at=datetime.utcnow() + timedelta(days=7),
            geo_captured_lat=55.7558,
            geo_captured_lng=37.6173,
        )
        session.add(visit1)
        await session.flush()
        
        visit2 = Visit(
            object_id=obj1.id,
            customer_id=customer2.id,
            engineer_id=engineer1.id,
            scheduled_at=datetime.utcnow() - timedelta(days=1, hours=6),
            started_at=datetime.utcnow() - timedelta(days=1, hours=6),
            finished_at=datetime.utcnow() - timedelta(days=1, hours=4),
            status=VisitStatus.DONE,
            interests=[InterestType.CCTV.value],
            outcome_text="Требуется консультация по тарифам",
            geo_captured_lat=55.7558,
            geo_captured_lng=37.6173,
        )
        session.add(visit2)
        await session.flush()
        
        visit3 = Visit(
            object_id=obj2.id,
            engineer_id=engineer2.id,
            scheduled_at=datetime.utcnow() + timedelta(hours=12),
            status=VisitStatus.PLANNED,
        )
        session.add(visit3)
        await session.flush()
        
        visit4 = Visit(
            object_id=obj3.id,
            customer_id=customer3.id,
            engineer_id=supervisor.id,
            scheduled_at=datetime.utcnow() - timedelta(days=3),
            started_at=datetime.utcnow() - timedelta(days=3),
            finished_at=datetime.utcnow() - timedelta(days=3, hours=-2),
            status=VisitStatus.DONE,
            interests=[InterestType.INTERNET.value, InterestType.CCTV.value],
            outcome_text="Успешно подключён",
            next_action_due_at=datetime.utcnow() + timedelta(days=7),
            geo_captured_lat=55.7458,
            geo_captured_lng=37.6073,
        )
        session.add(visit4)
        await session.flush()
        
        await session.commit()
        print("[OK] Тестовые данные заполнены:")
        print(f"   - Пользователи: {user_count + 4} (admin, supervisor, 2 engineer)")
        print(f"   - Объекты: 3")
        print(f"   - Клиенты: 3")
        print(f"   - Визиты: 4")
        print("\nУчетные данные:")
        print("   Admin: admin@example.com / admin123")
        print("   Supervisor: supervisor@example.com / supervisor123")
        print("   Engineer: engineer1@example.com / engineer123")
        print("   Engineer: engineer2@example.com / engineer123")
    
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(seed_test_data())

