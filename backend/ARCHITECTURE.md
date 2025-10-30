# Архитектура бэкенда CRM

## Структура проекта

```
backend/
├── app/
│   ├── api/                    # API слой
│   │   └── v1/
│   │       ├── routers/        # FastAPI роутеры
│   │       ├── schemas/        # Pydantic DTO
│   │       └── deps/          # Зависимости (RBAC, etc)
│   ├── core/                   # Ядро приложения
│   │   ├── config.py          # Настройки (pydantic-settings)
│   │   ├── security.py        # JWT, хеширование паролей
│   │   ├── errors.py          # Обработка ошибок
│   │   ├── pagination.py      # Утилиты пагинации
│   │   └── rate_limit.py      # Rate limiting
│   ├── domain/                 # Доменный слой
│   │   ├── entities/          # Чистые доменные модели
│   │   └── services/          # Бизнес-логика (use-cases)
│   ├── infrastructure/         # Инфраструктура
│   │   ├── db/
│   │   │   ├── base.py        # Engine, session
│   │   │   ├── models.py      # SQLAlchemy ORM
│   │   │   ├── repositories/  # Репозитории
│   │   │   └── uow.py         # Unit of Work
│   │   ├── cache/             # Redis клиент
│   │   └── queues/            # RQ задачи
│   ├── services/              # Сервисы приложения
│   │   └── excel_exporter.py  # Экспорт XLSX
│   ├── middlewares/           # Middleware
│   │   ├── logging.py
│   │   └── request_id.py
│   └── main.py                 # FastAPI app
├── alembic/                    # Миграции БД
├── scripts/                    # Утилиты
│   └── create_admin.py
├── tests/                      # Тесты
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
├── alembic.ini
└── .env
```

## Основные компоненты

### 1. Core (Ядро)

- **config.py**: Настройки через pydantic-settings, переменные окружения
- **security.py**: JWT генерация/валидация, хеширование паролей, scopes
- **errors.py**: Единый обработчик ошибок с кодами и сообщениями
- **pagination.py**: Утилиты для page-based и cursor-based пагинации
- **rate_limit.py**: Rate limiting через Redis

### 2. Infrastructure (Инфраструктура)

#### Database
- **base.py**: Async engine, session factory, базовый класс для моделей
- **models.py**: SQLAlchemy ORM модели (User, Object, Customer, Visit, etc.)
- **repositories/**: Репозитории для доступа к данным
- **uow.py**: Unit of Work паттерн для транзакций

#### Cache & Queues
- **cache/redis_client.py**: Redis клиент для кэша
- **queues/rq_tasks.py**: RQ задачи для фоновой обработки

### 3. API Layer

#### Routers
- **auth.py**: Авторизация (POST /token, POST /refresh)
- **users.py**: Управление пользователями (CRUD, GET /me)
- **objects.py**: Объекты (список, создание, обновление)
- **customers.py**: Клиенты
- **visits.py**: Визиты
- **dictionaries.py**: Справочники (города, районы)

#### Schemas (Pydantic)
- DTO для всех сущностей (Create, Update, Out)
- Валидация на уровне схем
- Типизация с помощью Python types

#### Dependencies
- **security.py**: get_current_user, require_roles, require_scopes

### 4. Domain Layer

- **entities/**: Чистые доменные модели (без ORM)
- **services/**: Бизнес-логика (use-cases)

### 5. Services

- **excel_exporter.py**: Генерация XLSX отчётов через openpyxl

## Паттерны

### Repository Pattern
- Абстракция доступа к данным
- Базовый репозиторий с CRUD операциями
- Специализированные репозитории (UserRepository, ObjectRepository)

### Unit of Work
- Инкапсулирует транзакции БД
- Отдаёт репозитории через контекстный менеджер
- Автоматический commit/rollback

### Service Layer
- Бизнес-логика вне контроллеров/репозиториев
- Use-cases для сложных операций

### RBAC (Role-Based Access Control)
- Роли: ADMIN, SUPERVISOR, ENGINEER
- Scopes для детального контроля доступа
- Зависимости FastAPI для проверки прав

## Безопасность

1. **JWT авторизация**:
   - Access token (30 мин)
   - Refresh token (14 дней)
   - OAuth2 Password Flow

2. **Пароли**:
   - bcrypt хеширование
   - Минимум 8 символов

3. **RBAC**:
   - Проверка ролей через зависимости
   - Scopes для детального доступа

4. **Rate Limiting**:
   - Redis token bucket
   - Настраиваемые лимиты

5. **Optimistic Locking**:
   - Поле `version` в моделях
   - Конфликты разрешаются через 409 Conflict

## Миграции

- **Alembic** для управления схемой БД
- Автогенерация миграций через `alembic revision --autogenerate`
- Поддержка async SQLAlchemy
- **Важно**: Индексы из `__table_args__` автоматически попадают в миграции
- При переходе на PostgreSQL — отдельные миграции для GIST/GIN/BRIN

**Руководство**: [MIGRATIONS.md](../MIGRATIONS.md)

## Тестирование

- pytest для юнит-тестов
- httpx для интеграционных тестов API
- factory-boy для тестовых данных

## Развёртывание

- **Docker Compose**: API, Worker, Redis
- **Переменные окружения**: .env файл
- **Health checks**: /health endpoint

## Офлайн-синхронизация

### Контракт `/sync/batch`

**Запрос:**
```json
{
  "items": [
    {
      "client_generated_id": "550e8400-e29b-41d4-a716-446655440000",
      "table_name": "objects",
      "payload": { "address": "...", "city_id": "..." },
      "updated_at": "2025-01-15T10:00:00Z",
      "version": 5
    }
  ],
  "force": false
}
```

**Успешный ответ (200):**
```json
{
  "results": [
    {
      "client_generated_id": "550e8400-e29b-41d4-a716-446655440000",
      "server_id": "123e4567-e89b-12d3-a456-426614174000",
      "status": "created|updated",
      "server_version": 6
    }
  ],
  "conflicts_count": 0,
  "errors_count": 0
}
```

**Конфликт (409):**
```json
{
  "error": {
    "code": "CONFLICT",
    "message": "Version conflict for objects",
    "details": {
      "diff": {
        "expected_version": 5,
        "current_version": 7,
        "server_data": { "address": "new", "status": "DONE" },
        "client_data": { "address": "old", "status": "NEW" },
        "diff": {
          "address": { "server": "new", "client": "old" },
          "status": { "server": "DONE", "client": "NEW" }
        }
      },
      "resolution_hints": {
        "code": "STALE_VERSION",
        "strategy": "merge|force|reject"
      }
    }
  }
}
```

**Коды конфликтов:**
- `STALE_VERSION` — версия на сервере новее (оптимистическая блокировка)
- `HARD_CONFLICT` — конфликт данных (разные значения критичных полей)

**Разрешение конфликтов:**
1. Переотправить с `force=true` (последняя версия побеждает)
2. Применить merge на клиенте по `diff`
3. Получить актуальную версию через `GET /sync/changes`

### Контракт `/sync/changes`

**Запрос:**
```
GET /sync/changes?since=2025-01-15T10:00:00Z&tables=objects,visits&limit=1000
```

**Ответ:**
```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "table_name": "objects",
      "action": "update",
      "data": { "address": "...", "version": 7 },
      "updated_at": "2025-01-15T11:00:00Z",
      "version": 7
    }
  ],
  "has_more": false,
  "next_cursor": "2025-01-15T11:00:00Z"
}
```

## Единый контракт фильтров

Все списковые эндпойнты поддерживают единый формат:

### Параметры запроса

- `q` (string) — текстовый поиск по основным полям
- `filters[field]=value` — фильтры по конкретным полям
- `sort=-updated_at,+city` — сортировка (префикс `-` desc, `+` asc)
- `page=1&limit=20` — page-based пагинация
- ИЛИ `cursor=...&size=20` — cursor-based пагинация

### Примеры

**Objects:**
```
GET /objects?q=Пушкина&filters[city_id]=...&filters[status]=NEW&sort=-updated_at,+address&page=1&limit=20
```

**Visits:**
```
GET /visits?filters[engineer_id]=...&filters[date_from]=2025-01-01&filters[date_to]=2025-01-31&sort=-scheduled_at
```

**Customers:**
```
GET /customers?q=Иван&filters[object_id]=...&filters[rating_min]=3&sort=-updated_at
```

### Ответ (page-based):
```json
{
  "items": [...],
  "page": 1,
  "limit": 20,
  "total": 150,
  "pages": 8,
  "has_next": true,
  "has_prev": false
}
```

### Ответ (cursor-based):
```json
{
  "items": [...],
  "next_cursor": "2025-01-15T10:00:00Z",
  "has_more": true
}
```

## PII-политика и маскирование

### Поля PII

- **Телефоны** (`phone`) — клиенты, пользователи
- **Email** (`email`) — пользователи
- **Персональные данные** (`full_name`, `portrait_text`) — клиенты

### Правила доступа

- **ADMIN** — полный доступ ко всем PII
- **SUPERVISOR** — полный доступ к PII своих городов
- **ENGINEER** — маскированное отображение (телефон: `+7 (***) ***-**89`)

### Маскирование в ответах

- Автоматическое применение в роутерах через `PIIFieldsMixin`
- Проверка через `has_pii_access = role == ADMIN or role == SUPERVISOR`
- Формат маскирования: `mask_phone("+79123456789") → "+7 (***) ***-**89"`

### Аудит и PII

- **Телефоны и email** НЕ логируются в `AuditLog.before_json/after_json` в открытом виде
- Вместо этого сохраняются маскированные версии или хэши
- Политика: исключение полей `phone`, `email`, `hashed_password` из логов аудита

## Экспорт отчётов

### Контракт `/reports/export`

**Создание задачи:**
```json
POST /reports/export
{
  "entity": "objects",
  "filters": { "city_id": "...", "status": "NEW" },
  "columns": ["id", "address", "status"],
  "sort": { "updated_at": "desc" }
}
```

**Ответ:**
```json
{
  "id": "job-uuid",
  "status": "pending",
  "created_at": "2025-01-15T10:00:00Z"
}
```

### Дедупликация

- Ключ: `hash(filters + columns + sort + user_id)`
- Если идентичная задача в статусе `pending/processing` за последние 5 минут — возвращается существующая job
- Предотвращает дублирование тяжёлых экспортов

### Rate Limiting

- **Глобальный лимит**: 10 задач на пользователя за 5 минут
- **Endpoint**: `/reports/export` защищён через Redis rate limiter
- При превышении: `429 Too Many Requests`

### Хранение файлов

- **TTL**: 7 дней (удаление старых отчётов)
- **Путь**: `./data/reports/report_{job_id}_{entity}_{timestamp}.xlsx`
- **Очистка**: периодическая задача (cron) или при запросе через `GET /reports/jobs/{id}/download` проверяется TTL

### Статусы job

- `pending` — задача создана, ожидает обработки
- `processing` — обработка в очереди
- `done` — файл готов к скачиванию
- `failed` — ошибка (см. `error_message`)

### Политика ретраев и dead-letter

**Ретраи фоновых задач:**
- Максимум 3 попытки с экспоненциальной задержкой (1мин, 2мин, 4мин)
- При неудаче после всех попыток — статус `failed`, запись в `error_message`
- Dead-letter queue не используется (задачи остаются в БД со статусом `failed`)

**Мониторинг очереди:**
- Health check worker: `GET /worker/health` (длина очереди, количество воркеров)
- Readiness check: `GET /worker/ready` (Redis доступен)
- Метрики: `GET /metrics` (queue_length, database, redis status)

**TTL отчётов:**
- Автоматическая очистка файлов старше 7 дней
- Периодическая задача (cron) или проверка при скачивании
- Удаление старых записей из `report_jobs` с статусом `done`

## Индексация БД

### Уникальные индексы

- `users.email` — UNIQUE (уже через `unique=True`)
- `customers.phone` — UNIQUE (опционально, если требуется)
- `sync_tokens.client_generated_id` — UNIQUE

### Индексы по фильтрам

**Objects:**
- `(city_id)` — фильтрация по городу
- `(district_id)` — фильтрация по району
- `(status)` — фильтрация по статусу
- `(city_id, status)` — составной для частых запросов
- `(updated_at)` — сортировка и диапазоны дат
- `(responsible_user_id)` — фильтрация по ответственному

**Visits:**
- `(engineer_id)` — фильтрация по инженеру
- `(object_id)` — фильтрация по объекту
- `(status)` — фильтрация по статусу
- `(scheduled_at)` — диапазоны дат планирования
- `(finished_at)` — диапазоны завершения
- `(engineer_id, scheduled_at)` — составной для маршрутов
- `(object_id, status)` — составной для отчётов

**Customers:**
- `(phone)` — уникальный индекс (если требуется)
- `(object_id)` — фильтрация по объекту
- `(unit_id)` — фильтрация по квартире
- `(updated_at)` — сортировка и диапазоны

**AuditLog:**
- `(entity_type, entity_id, occurred_at)` — просмотр истории по сущности
- `(actor_id, occurred_at)` — действия пользователя
- `(occurred_at)` — диапазоны дат (уже есть через `index=True`)

**SyncToken:**
- `(client_generated_id)` — UNIQUE
- `(table_name, last_seen_at)` — составной для очистки старых токенов
- `(server_id)` — поиск по серверному ID

**ReportJob:**
- `(owner_id, created_at)` — история задач пользователя
- `(status, created_at)` — поиск pending/processing задач

### Геолокация (будущее)

**SQLite (текущее):**
- `(gps_lat, gps_lng)` — обычные индексы
- **Ограничение**: Гео-поиск в SQLite **приблизительный** (линейный поиск по координатам)
- Для точного поиска по радиусу/области требуется PostgreSQL с PostGIS

**PostgreSQL (прод):**
- `GIST` индекс через PostGIS для точного поиска по радиусу/области
- Пример: `CREATE INDEX idx_objects_geo ON objects USING GIST (point(gps_lng, gps_lat))`
- SQL: `SELECT * FROM objects WHERE ST_DWithin(point(gps_lng, gps_lat), point(37.6173, 55.7558), 1000)`

### Версионирование

- `version` и `updated_at` индексируются для `sync/changes` и проверок конфликтов
- Уже есть через поля в моделях

### Итоговая таблица индексов

| Таблица | Индексы | Назначение |
|---------|---------|------------|
| **Objects** | `city_id`, `district_id`, `status`, `(city_id, status)`, `updated_at`, `last_visit_at`, `version`, `(gps_lat, gps_lng)` | Фильтры, сортировка, гео-поиск |
| **Visits** | `engineer_id`, `object_id`, `status`, `scheduled_at`, `finished_at`, `next_action_due_at`, `(engineer_id, scheduled_at)`, `(object_id, status)`, `version` | Маршруты, отчёты, напоминания |
| **Customers** | `phone` UNIQUE, `object_id`, `unit_id`, `updated_at` | Поиск по телефону, фильтры |
| **AuditLog** | `(entity_type, entity_id, occurred_at)`, `(actor_id, occurred_at)`, `occurred_at` | История изменений |
| **SyncToken** | `client_generated_id` UNIQUE, `(table_name, last_seen_at)`, `server_id` | Синхронизация |
| **ReportJob** | `(owner_id, created_at)`, `(status, created_at)` | История задач |

**Всего индексов**: ~25 (оптимально для проектов такого масштаба)

## Redis — использование

### Обязательные компоненты

1. **Очереди RQ** — фоновые задачи (экспорт XLSX, аналитика)
   - Без Redis очереди не работают
   - Используется в `docker-compose.yml`

2. **Rate Limiting** — защита эндпойнтов
   - `/auth/token` — 5 попыток в минуту
   - `/reports/export` — 10 задач за 5 минут
   - Можно отключить через `RATE_LIMIT_ENABLED=false` в `.env`

### Опциональные компоненты

3. **Кэш справочников** — города, районы (TTL 10-60 мин)
4. **Кэш аналитики** — предвычисленные агрегаты
5. **Token blacklist** — для logout (если реализован)

### Конфигурация

- **Dev**: можно обойтись без Redis для чистого API (отключить rate limiting и очереди)
- **Prod**: Redis обязателен для очередей и rate limiting

## Дальнейшее развитие

1. ✅ Реализовать полные роутеры для customers, visits
2. ✅ Добавить доменные сервисы для бизнес-логики
3. ✅ Реализовать офлайн-синхронизацию (sync/batch)
4. ✅ Добавить аудит логирование в middleware
5. ✅ Реализовать экспорт отчётов через очередь
6. Добавить аналитику и предварительные вычисления
7. Интеграция с картами (геокодирование)
8. Push-уведомления
9. Тесты (unit + integration)

