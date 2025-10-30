# CRM Backend API

FastAPI backend для CRM системы управления объектами, визитами и клиентами.

## Технологический стек

- **FastAPI** 0.115+ - веб-фреймворк
- **SQLAlchemy** 2.0+ - ORM
- **Alembic** - миграции БД
- **Pydantic** v2 - валидация данных
- **JWT** - авторизация
- **Redis** - кэш и очереди
- **RQ** - фоновые задачи
- **openpyxl** - экспорт XLSX

## Установка

### 1. Создать виртуальное окружение

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows
```

### 2. Установить зависимости

```bash
pip install -r requirements.txt
```

### 3. Настроить окружение

```bash
cp .env.example .env
# Отредактировать .env (JWT_SECRET, DATABASE_URL и т.д.)
```

### 4. Создать базу данных

```bash
# Создать директории
mkdir -p data/files data/reports

# Применить миграции
alembic upgrade head
```

### 5. Запустить сервер

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Использование Docker

```bash
docker-compose up -d
```

## Структура проекта

```
app/
  api/v1/         - API роутеры и схемы
  core/           - Конфигурация, безопасность, утилиты
  domain/         - Доменные сущности и сервисы
  infrastructure/ - Репозитории, БД, файлы, Redis
  services/       - Сервисы экспорта, аналитики
  main.py         - Точка входа FastAPI
```

## API Документация

После запуска доступна:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Основные эндпойнты

- `POST /api/v1/auth/token` - авторизация (получить JWT)
- `GET /api/v1/users/me` - текущий пользователь
- `GET /api/v1/objects` - список объектов (с фильтрами и пагинацией)
- `POST /api/v1/visits` - создать визит
- `POST /api/v1/reports/export` - экспорт отчёта (создание задачи)
- `GET /api/v1/reports/jobs` - список задач экспорта
- `GET /api/v1/reports/jobs/{id}/download` - скачать готовый отчёт
- `POST /api/v1/sync/batch` - офлайн-синхронизация (batch upsert)
- `GET /api/v1/sync/changes` - получить изменения с сервера
- `GET /api/v1/audit` - просмотр истории изменений

Подробные примеры в [QUICKSTART.md](QUICKSTART.md)

## Роли

- **ADMIN** - полный доступ
- **SUPERVISOR** - управление инженерами и объектами
- **ENGINEER** - создание визитов, работа с клиентами

## Redis

**Обязателен для:**
- Очереди фоновых задач (RQ) — экспорт XLSX
- Rate limiting на критичных эндпойнтах

**Опционален для:**
- Кэш справочников и аналитики
- Token blacklist (если реализован)

**В dev можно отключить:**
- Установить `RATE_LIMIT_ENABLED=false` в `.env`
- Очереди будут недоступны, но API работает

## Индексы БД

Детальная документация по индексам: [INDEXES.md](INDEXES.md)

**Что такое индексы?**  
Индексы — это "оглавление" для таблиц БД. Они ускоряют фильтры/сортировки/джоины за счёт упорядоченных ссылок на строки по выбранным полям. Минус: немного больше места и чуть медленнее вставки/апдейты.

**Основные индексы в проекте:**
- **Фильтры**: `city_id`, `district_id`, `status`, `engineer_id`, `object_id`
- **Составные**: `(city_id, status)`, `(engineer_id, scheduled_at)`, `(entity_type, entity_id, occurred_at)`
- **Версионирование**: `version`, `updated_at` — для синхронизации
- **Гео**: `(gps_lat, gps_lng)` — для карт (в Postgres будет GIST)
- **Поиск**: `phone` UNIQUE — быстрый поиск клиентов
- **Напоминания**: `next_action_due_at` — выборки "к прозвону"

## Тестирование

```bash
pytest
pytest --cov=app tests/
```

## Health checks

**API:**
- `GET /health` — базовая проверка работоспособности
- `GET /ready` — готовность (БД доступна)
- `GET /metrics` — метрики (БД, Redis, очередь)

**Worker (RQ):**
- `GET /worker/health` — проверка worker (очередь, воркеры)
- `GET /worker/ready` — готовность worker (Redis доступен)

**Пример:**
```bash
curl http://localhost:8000/health
curl http://localhost:8000/worker/health
```

## Smoke-тесты (быстрые проверки)

Подробное руководство: [SMOKE_TESTS.md](SMOKE_TESTS.md)

**Быстрая проверка:**

1. **Sync happy-path**: Создать объект офлайн → проверить server_id → получить изменения
2. **Sync conflict**: Обновить с устаревшей версией → получить 409 с diff → разрешить с force=true
3. **Отчёты**: Создать задачу → проверить статус → скачать файл → проверить аудит
4. **PII-RBAC**: ENGINEER видит маскированные телефоны, ADMIN — полные
5. **Optimistic locking**: PATCH с правильной версией → успех, с устаревшей → 409

Все тесты с примерами curl в [SMOKE_TESTS.md](SMOKE_TESTS.md)

## Миграции

Подробное руководство: [MIGRATIONS.md](MIGRATIONS.md)

### Первая миграция (создание схемы)

```bash
# Сгенерировать миграцию с индексами
alembic revision --autogenerate -m "initial schema with indexes"

# Проверить созданный файл в alembic/versions/

# Применить
alembic upgrade head
```

### Последующие миграции

```bash
# Создать новую миграцию
alembic revision --autogenerate -m "description"

# Применить миграции
alembic upgrade head

# Откатить
alembic downgrade -1
```

**Важно**: После добавления индексов в `__table_args__` всегда генерируйте миграцию через `alembic revision --autogenerate`.

### Миграция на PostgreSQL (prod)

При переходе на PostgreSQL создайте отдельную миграцию для специализированных индексов (GIST/GIN/BRIN):

```bash
# Создать миграцию для Postgres
alembic revision -m "migrate to postgresql with GIST indexes"

# В файле миграции добавить GIST индексы для гео-поиска
# Подробнее: см. MIGRATIONS.md → "Миграция на PostgreSQL"
```

**Руководство**: [MIGRATIONS.md](MIGRATIONS.md) → раздел "Миграция на PostgreSQL"

