# Быстрый старт

## 1. Установка зависимостей

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

pip install -r requirements.txt
```

## 2. Настройка окружения

Создайте файл `.env` (скопируйте из `.env.example` или используйте готовый):

```bash
cp .env.example .env
```

Отредактируйте `.env`:
- `JWT_SECRET` - установите безопасный ключ (минимум 32 символа)
- `DATABASE_URL` - путь к базе данных
- `REDIS_URL` - URL Redis (если используете)

## 3. Создание базы данных

```bash
# Создать директории
mkdir -p data/files data/reports

# Сгенерировать первую миграцию (с индексами)
alembic revision --autogenerate -m "initial schema with indexes"

# Проверить созданный файл миграции в alembic/versions/

# Применить миграции
alembic upgrade head
```

**Примечание**: Если миграция уже существует, просто выполните `alembic upgrade head`.

## 4. Заполнение справочников (seed)

```bash
# Заполнить города и районы тестовыми данными
python scripts/seed_dictionaries.py
```

Это создаст:
- Города: Москва, Санкт-Петербург, Казань
- Районы для каждого города (по 3-5 районов)

**Примечание**: Скрипт пропускает заполнение, если данные уже есть в БД.

## 5. Создание администратора

```bash
python scripts/create_admin.py admin@example.com password123 "Admin User"
```

## 6. Запуск сервера

### Локально

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
docker-compose up -d
```

## 7. Проверка

- API документация: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

## 8. Авторизация

```bash
# Получить токен
curl -X POST "http://localhost:8000/api/v1/auth/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=password123"
```

Ответ:
```json
{
  "access_token": "eyJ...",
  "refresh_token": "eyJ...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

Используйте `access_token` в заголовке:
```
Authorization: Bearer <access_token>
```

## 8. Примеры запросов

### Получить текущего пользователя

```bash
curl -X GET "http://localhost:8000/api/v1/users/me" \
  -H "Authorization: Bearer <access_token>"
```

### Создать объект

```bash
curl -X POST "http://localhost:8000/api/v1/objects" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "MKD",
    "address": "ул. Пушкина, д. 12",
    "city_id": "<city_id>",
    "status": "NEW"
  }'
```

### Список объектов

```bash
curl -X GET "http://localhost:8000/api/v1/objects?page=1&limit=20&filters[status]=NEW&sort=-updated_at" \
  -H "Authorization: Bearer <access_token>"
```

### Офлайн-синхронизация

**Batch-синхронизация:**
```bash
curl -X POST "http://localhost:8000/api/v1/sync/batch" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "items": [
      {
        "client_generated_id": "550e8400-e29b-41d4-a716-446655440000",
        "table_name": "objects",
        "payload": {
          "address": "ул. Новая, д. 1",
          "city_id": "...",
          "status": "NEW"
        },
        "updated_at": "2025-01-15T10:00:00Z",
        "version": 1
      }
    ],
    "force": false
  }'
```

**Получить изменения с сервера:**
```bash
curl -X GET "http://localhost:8000/api/v1/sync/changes?since=2025-01-15T10:00:00Z&tables=objects,visits&limit=1000" \
  -H "Authorization: Bearer <access_token>"
```

### Экспорт отчёта

**Создать задачу экспорта:**
```bash
curl -X POST "http://localhost:8000/api/v1/reports/export" \
  -H "Authorization: Bearer <access_token>" \
  -H "Content-Type: application/json" \
  -d '{
    "entity": "objects",
    "filters": { "status": "NEW" },
    "columns": ["id", "address", "status"]
  }'
```

**Проверить статус:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/jobs/<job_id>" \
  -H "Authorization: Bearer <access_token>"
```

**Скачать готовый отчёт:**
```bash
curl -X GET "http://localhost:8000/api/v1/reports/jobs/<job_id>/download" \
  -H "Authorization: Bearer <access_token>" \
  -o report.xlsx
```

### Аудит

**Список записей аудита:**
```bash
curl -X GET "http://localhost:8000/api/v1/audit?entity_type=object&since=2025-01-15T00:00:00Z&page=1&limit=20" \
  -H "Authorization: Bearer <access_token>"
```

## Структура данных

Перед использованием нужно заполнить справочники:

1. **Города** (cities):
   - Москва
   - Санкт-Петербург
   - и т.д.

2. **Районы** (districts):
   - Центральный
   - Северный
   - и т.д.

Можно добавить через API (если реализовано) или напрямую в БД.

## Следующие шаги

1. Заполнить справочники (города, районы)
2. Создать пользователей разных ролей
3. Создать объекты
4. Создать визиты
5. Работать с клиентами

## Troubleshooting

### Ошибка подключения к БД

Убедитесь, что директория `data/` существует и доступна для записи.

### Ошибка подключения к Redis

Если Redis не установлен, можно временно отключить rate limiting в `.env`:
```
RATE_LIMIT_ENABLED=false
```

### Ошибка миграций

**Важно**: После добавления индексов всегда генерируйте миграцию:

```bash
# Проверить текущую версию
alembic current

# Сгенерировать миграцию
alembic revision --autogenerate -m "description"

# Применить
alembic upgrade head
```

Убедитесь, что все модели импортированы в `alembic/env.py`.

### Индексы не созданы

Если индексы не создаются:
1. Проверьте, что они добавлены в `__table_args__` моделей
2. Убедитесь, что миграция сгенерирована через `alembic revision --autogenerate`
3. Проверьте созданный файл миграции в `alembic/versions/`
4. Примените: `alembic upgrade head`

### Проблемы с зависимостями

Обновите зависимости:
```bash
pip install --upgrade -r requirements.txt
```

## Smoke-тесты

После настройки запустите smoke-тесты из [SMOKE_TESTS.md](../SMOKE_TESTS.md) для проверки функциональности.

