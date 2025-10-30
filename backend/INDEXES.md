# Индексы базы данных

Документация по индексам для оптимизации запросов и фильтрации.

## Общие принципы

- Индексы создаются через SQLAlchemy `Index()` в `__table_args__`
- Автоматическая генерация через Alembic миграции
- При миграции на PostgreSQL добавятся специализированные индексы (GIST для гео)

## Таблица: Objects

**Индексы для фильтрации:**
- `ix_objects_city_id` — фильтрация по городу
- `ix_objects_district_id` — фильтрация по району
- `ix_objects_status` — фильтрация по статусу
- `ix_objects_city_status` — составной (город + статус) для частых запросов
- `ix_objects_responsible_user` — фильтрация по ответственному инженеру

**Индексы для сортировки и диапазонов:**
- `ix_objects_updated_at` — сортировка и поиск изменений
- `ix_objects_last_visit_at` — выборки по периоду визитов
- `ix_objects_version` — оптимистические блокировки и синхронизация

**Геолокация:**
- `ix_objects_gps` — составной индекс `(gps_lat, gps_lng)` для гео-поиска (SQLite: обычный, Postgres: будет GIST)

## Таблица: Visits

**Индексы для фильтрации:**
- `ix_visits_engineer_id` — фильтрация по инженеру
- `ix_visits_object_id` — фильтрация по объекту
- `ix_visits_status` — фильтрация по статусу

**Индексы для диапазонов дат:**
- `ix_visits_scheduled_at` — диапазоны планирования
- `ix_visits_finished_at` — диапазоны завершения
- `ix_visits_next_action_due_at` — выборки "к прозвону" (напоминания)

**Составные индексы:**
- `ix_visits_engineer_scheduled` — маршруты инженера на дату
- `ix_visits_object_status` — визиты объекта по статусу

**Версионирование:**
- `ix_visits_version` — проверки конфликтов

## Таблица: Customers

**Индексы:**
- `ix_customers_object_id` — фильтрация по объекту
- `ix_customers_unit_id` — фильтрация по квартире
- `ix_customers_updated_at` — сортировка и диапазоны

**Уникальные:**
- `phone` — UNIQUE индекс для быстрого поиска по телефону (через `unique=True`)

**Примечание**: UNIQUE на `phone` включён в модели. Если бизнес-логика не требует уникальности (несколько клиентов с одним телефоном), можно убрать `unique=True`, оставив только обычный индекс для поиска.

## Таблица: AuditLog

**Индексы для просмотра истории:**
- `ix_audit_entity_type_id_date` — история изменений конкретной сущности
- `ix_audit_actor_date` — действия пользователя за период
- `occurred_at` — диапазоны дат (через `index=True`)

## Таблица: SyncToken

**Индексы для синхронизации:**
- `client_generated_id` — UNIQUE (через `unique=True`)
- `server_id` — поиск по серверному ID
- `ix_sync_token_table_seen` — очистка старых токенов

## Таблица: ReportJob

**Индексы:**
- `ix_report_job_owner_created` — история задач пользователя
- `ix_report_job_status_created` — поиск pending/processing задач

## Уникальные индексы

- `users.email` — UNIQUE
- `sync_tokens.client_generated_id` — UNIQUE
- `customers.phone` — UNIQUE (опционально)

## Геолокация (будущее)

**SQLite (текущее):**
- Обычные индексы на `(gps_lat, gps_lng)`
- **⚠️ Ограничение**: Гео-поиск в SQLite **приблизительный** (без точного поиска по радиусу)
- Для фильтрации по координатам используются обычные WHERE условия
- Для продакшена с картами требуется PostgreSQL + PostGIS

**PostgreSQL (прод):**
```sql
-- Создание GIST индекса
CREATE INDEX idx_objects_geo ON objects USING GIST (
  point(gps_lng, gps_lat)
);
```

Для поиска по радиусу (точный поиск):
```sql
SELECT * FROM objects
WHERE ST_DWithin(
  point(gps_lng, gps_lat),
  point(37.6173, 55.7558),
  1000  -- радиус в метрах
);
```

**При миграции на PostgreSQL:**
- Создать отдельную миграцию для GIST индексов
- Установить расширение PostGIS: `CREATE EXTENSION postgis;`
- Пересоздать индексы через Alembic или вручную

## Миграция на PostgreSQL

При переходе на PostgreSQL:

1. **BRIN индексы** для временных полей (большие таблицы):
   ```python
   Index("ix_audit_occurred_at_brin", AuditLog.occurred_at, postgresql_using="brin")
   ```

2. **GIN индексы** для JSON полей (интересы, теги):
   ```python
   Index("ix_customers_interests_gin", Customer.interests, postgresql_using="gin")
   ```

3. **GIST индексы** для геолокации (см. выше)

4. **Частичные индексы** для активных записей:
   ```python
   Index("ix_objects_active", Object.status, postgresql_where=Object.status != "REJECTED")
   ```

