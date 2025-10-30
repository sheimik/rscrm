# Миграции БД

Руководство по работе с миграциями Alembic.

## Первая миграция (создание схемы и индексов)

### 1. Сгенерировать миграцию

```bash
cd backend
alembic revision --autogenerate -m "initial schema with indexes"
```

Это создаст файл миграции в `alembic/versions/` с:
- Всеми таблицами (users, objects, visits, customers, etc.)
- Всеми индексами из `__table_args__`
- Foreign keys и constraints

### 2. Проверить миграцию

Откройте созданный файл и проверьте:
- Все индексы присутствуют
- Типы данных корректны
- Foreign keys настроены правильно

### 3. Применить миграцию

```bash
alembic upgrade head
```

## Последующие миграции

### Добавление нового поля/индекса

```bash
# 1. Добавьте поле/индекс в models.py
# 2. Сгенерируйте миграцию
alembic revision --autogenerate -m "add field X to table Y"

# 3. Проверьте файл миграции
# 4. Примените
alembic upgrade head
```

### Откат миграции

```bash
# Откатить последнюю миграцию
alembic downgrade -1

# Откатить до конкретной версии
alembic downgrade <revision_id>
```

## Специальные миграции

### Миграция на PostgreSQL

При переходе с SQLite на PostgreSQL:

1. **Создать базовую миграцию для Postgres:**
```bash
alembic revision -m "migrate to postgresql"
```

2. **В файле миграции добавить GIST индексы:**
```python
def upgrade() -> None:
    # Установить расширение PostGIS
    op.execute("CREATE EXTENSION IF NOT EXISTS postgis;")
    
    # Удалить старый индекс (если был)
    op.drop_index("ix_objects_gps", table_name="objects")
    
    # Создать GIST индекс для гео-поиска
    op.execute("""
        CREATE INDEX ix_objects_gps_gist ON objects 
        USING GIST (point(gps_lng, gps_lat))
    """)
    
    # Аналогично для других таблиц с гео
```

3. **Добавить BRIN индексы для больших таблиц:**
```python
# Для AuditLog (если таблица большая)
op.execute("""
    CREATE INDEX ix_audit_occurred_at_brin ON audit_logs 
    USING BRIN (occurred_at)
""")
```

4. **Добавить GIN индексы для JSON полей:**
```python
# Для поиска по interests в customers
op.execute("""
    CREATE INDEX ix_customers_interests_gin ON customers 
    USING GIN (interests)
""")
```

## Проверка миграций

### Просмотр текущей версии

```bash
alembic current
```

### История миграций

```bash
alembic history
```

### Проверка отката

```bash
# Посмотреть, что будет откачено
alembic downgrade -1 --sql

# Если всё ок, выполнить
alembic downgrade -1
```

## Важные замечания

1. **Индексы через `__table_args__`** автоматически попадают в автогенерацию
2. **UNIQUE constraints** также генерируются автоматически
3. **При переходе на Postgres** некоторые индексы нужно пересоздать вручную (GIST/GIN/BRIN)
4. **Всегда проверяйте** сгенерированный файл миграции перед применением

## Примеры

### Добавление нового индекса

```python
# 1. В models.py добавить:
__table_args__ = (
    Index("ix_new_index", "field_name"),
)

# 2. Сгенерировать миграцию
alembic revision --autogenerate -m "add index ix_new_index"

# 3. Применить
alembic upgrade head
```

### Изменение существующего поля

```python
# 1. Изменить тип/ограничения в models.py
# 2. Сгенерировать миграцию
alembic revision --autogenerate -m "change field type"

# 3. Проверить и применить
alembic upgrade head
```

