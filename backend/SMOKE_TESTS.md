# Smoke-тесты

Быстрые проверки для валидации критичных функций.

## 1. Sync happy-path

**Цель**: Проверить базовую синхронизацию

```bash
# 1. Получить токен
TOKEN=$(curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password123" \
  | jq -r '.access_token')

# 2. Создать объект офлайн
curl -X POST "http://localhost:8000/api/v1/sync/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{
      "client_generated_id": "550e8400-e29b-41d4-a716-446655440000",
      "table_name": "objects",
      "payload": {
        "address": "ул. Тестовая, д. 1",
        "city_id": "...",
        "status": "NEW"
      },
      "updated_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
      "version": 1
    }]
  }'

# Ожидаемый результат:
# - status: 200
# - results[0].status: "created"
# - results[0].server_id: UUID
# - results[0].server_version: 1 или больше

# 3. Получить изменения
curl -X GET "http://localhost:8000/api/v1/sync/changes?since=2025-01-01T00:00:00Z&tables=objects&limit=100" \
  -H "Authorization: Bearer $TOKEN"

# Ожидаемый результат:
# - items содержит созданный объект
# - version совпадает
```

## 2. Sync conflict

**Цель**: Проверить обработку конфликтов версий

```bash
# 1. Получить существующий объект (запомнить version)
OBJECT=$(curl -X GET "http://localhost:8000/api/v1/objects/{id}" \
  -H "Authorization: Bearer $TOKEN")

CURRENT_VERSION=$(echo $OBJECT | jq -r '.version')

# 2. Попытаться обновить с устаревшей версией
curl -X POST "http://localhost:8000/api/v1/sync/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [{
      "client_generated_id": "...",
      "table_name": "objects",
      "payload": {"address": "новый адрес"},
      "updated_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",
      "version": '$(($CURRENT_VERSION - 1))'
    }]
  }'

# Ожидаемый результат:
# - status: 409 Conflict
# - error.code: "CONFLICT"
# - error.details.diff содержит:
#   - expected_version и current_version
#   - server_data и client_data
#   - diff по полям
#   - resolution_hints с кодом "STALE_VERSION"

# 3. Разрешить конфликт с force=true
curl -X POST "http://localhost:8000/api/v1/sync/batch" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [...],
    "force": true
  }'

# Ожидаемый результат:
# - status: 200
# - results[0].status: "updated"
```

## 3. Отчёты

**Цель**: Проверить полный цикл экспорта

```bash
# 1. Создать задачу экспорта
JOB=$(curl -X POST "http://localhost:8000/api/v1/reports/export" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "objects",
    "filters": {"status": "NEW"},
    "columns": ["id", "address", "status"]
  }')

JOB_ID=$(echo $JOB | jq -r '.id')

# Ожидаемый результат:
# - status: 201
# - job.status: "pending"

# 2. Проверить статус
curl -X GET "http://localhost:8000/api/v1/reports/jobs/$JOB_ID" \
  -H "Authorization: Bearer $TOKEN"

# Ожидаемый результат:
# - status меняется: pending → processing → done
# - file_path появляется при done

# 3. Скачать файл
curl -X GET "http://localhost:8000/api/v1/reports/jobs/$JOB_ID/download" \
  -H "Authorization: Bearer $TOKEN" \
  -o report.xlsx

# Ожидаемый результат:
# - Файл скачивается
# - Это валидный XLSX файл

# 4. Проверить аудит
curl -X GET "http://localhost:8000/api/v1/audit?action=EXPORT&entity_type=objects" \
  -H "Authorization: Bearer $TOKEN"

# Ожидаемый результат:
# - Есть запись EXPORT с правильными данными
```

## 4. PII-RBAC

**Цель**: Проверить маскирование PII по ролям

```bash
# 1. Получить клиента как ENGINEER
curl -X GET "http://localhost:8000/api/v1/customers/{id}" \
  -H "Authorization: Bearer $ENGINEER_TOKEN"

# Ожидаемый результат:
# - phone: "+7 (***) ***-**89" (маскирован)
# - full_name: полное (не маскируется)

# 2. Получить клиента как ADMIN
curl -X GET "http://localhost:8000/api/v1/customers/{id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Ожидаемый результат:
# - phone: "+79123456789" (полный)
# - full_name: полное

# 3. Проверить аудит (PII маскированы)
curl -X GET "http://localhost:8000/api/v1/audit?entity_type=customer&entity_id={id}" \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

**Пример ответа аудита с маскированным PII:**

```json
{
  "items": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "entity_type": "customer",
      "entity_id": "...",
      "action": "UPDATE",
      "actor_id": "...",
      "occurred_at": "2025-01-15T10:00:00Z",
      "before_json": {
        "phone": "+7 (***) ***-**89",
        "full_name": "Иван Иванов",
        "provider_rating": 4
      },
      "after_json": {
        "phone": "+7 (***) ***-**89",
        "full_name": "Иван Петров",
        "provider_rating": 5
      },
      "changes_summary": {
        "full_name": {"old": "Иван Иванов", "new": "Иван Петров"},
        "provider_rating": {"old": 4, "new": 5}
      }
    }
  ],
  "total": 1,
  "page": 1,
  "limit": 20
}
```

**Важно**: Телефон маскируется в `before_json` и `after_json` даже для ADMIN, так как аудит не должен хранить PII в открытом виде.

## 5. Оптимистические блокировки (PATCH)

**Цель**: Проверить version checking в PATCH (не только sync/batch)

```bash
# 1. Получить объект
OBJECT=$(curl -X GET "http://localhost:8000/api/v1/objects/{id}" \
  -H "Authorization: Bearer $TOKEN")

VERSION=$(echo $OBJECT | jq -r '.version')

# 2. Обновить с правильной версией
curl -X PATCH "http://localhost:8000/api/v1/objects/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"address\": \"новый адрес\",
    \"version\": $VERSION
  }"

# Ожидаемый результат:
# - status: 200
# - version увеличился на 1

# 3. Попытаться обновить с устаревшей версией
curl -X PATCH "http://localhost:8000/api/v1/objects/{id}" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"address\": \"другой адрес\",
    \"version\": $VERSION
  }"
```

**Пример ответа 409 Conflict в PATCH:**

```json
{
  "detail": "Object was modified by another user",
  "code": "CONFLICT",
  "details": {
    "diff": {
      "expected_version": 5,
      "current_version": 7,
      "resolution_hints": {
        "code": "STALE_VERSION",
        "strategy": "merge|force|reject",
        "message": "Server version is newer. Use force=true to overwrite or apply merge on client."
      }
    }
  }
}
```

**Ожидаемый результат:**
- status: 409 Conflict
- error.code: "CONFLICT"
- error.details.diff содержит:
  - `expected_version` и `current_version`
  - `resolution_hints` с кодом и стратегией

## 6. Использование индексов

**Цель**: Проверить, что индексы используются в запросах

```bash
# 1. Фильтрация по городу (использует ix_objects_city_id)
curl -X GET "http://localhost:8000/api/v1/objects?filters[city_id]=..." \
  -H "Authorization: Bearer $TOKEN"

# 2. Фильтрация по статусу (использует ix_objects_status)
curl -X GET "http://localhost:8000/api/v1/objects?filters[status]=NEW" \
  -H "Authorization: Bearer $TOKEN"

# 3. Составной фильтр (использует ix_objects_city_status)
curl -X GET "http://localhost:8000/api/v1/objects?filters[city_id]=...&filters[status]=NEW" \
  -H "Authorization: Bearer $TOKEN"

# 4. Поиск по телефону (использует UNIQUE индекс phone)
curl -X GET "http://localhost:8000/api/v1/customers?phone=+79123456789" \
  -H "Authorization: Bearer $TOKEN"

# 5. Напоминания "к прозвону" (использует ix_visits_next_action_due_at)
curl -X GET "http://localhost:8000/api/v1/visits?next_action_due=true" \
  -H "Authorization: Bearer $TOKEN"
```

## Проверка в БД

### SQLite

```bash
# Подключиться к БД
sqlite3 backend/data/crm.db

# Проверить индексы
.schema objects
.indexes objects

# Проверить использование индекса (EXPLAIN QUERY PLAN)
EXPLAIN QUERY PLAN SELECT * FROM objects WHERE city_id = '...';
```

### PostgreSQL (в будущем)

```sql
-- Проверить индексы
SELECT indexname, indexdef FROM pg_indexes WHERE tablename = 'objects';

-- Проверить использование индекса
EXPLAIN ANALYZE SELECT * FROM objects WHERE city_id = '...';
```

## Автоматизация

Можно создать скрипт для запуска всех тестов:

```bash
# backend/scripts/smoke_tests.sh
#!/bin/bash
source .env
export TOKEN=$(curl ... | jq -r '.access_token')

echo "Running smoke tests..."
# ... выполнение всех тестов
```

