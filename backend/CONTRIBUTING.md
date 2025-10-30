# Руководство по разработке

## Соглашения о коде

- **Типизация**: Все функции должны быть типизированы (type hints)
- **Документация**: Docstrings для всех публичных функций/классов
- **Ошибки**: Используйте `AppError` и подклассы из `app.core.errors`
- **Логирование**: Используйте `structlog` для структурированных логов

## Добавление нового эндпойнта

1. **Схема (Pydantic)**: `app/api/v1/schemas/{entity}.py`
2. **Роутер**: `app/api/v1/routers/{entity}.py`
3. **Регистрация**: Добавить в `app/api/v1/__init__.py`
4. **Тесты**: `tests/api/v1/test_{entity}.py`

## Фильтры и пагинация

Все списковые эндпойнты должны поддерживать:
- `q` — текстовый поиск
- `filters[field]=value` — фильтры
- `sort=-updated_at,+city` — сортировка
- `page/limit` — пагинация

Используйте утилиты из `app.core.filters` и `app.core.pagination`.

## Безопасность

- **PII поля**: Маскируйте телефоны/email для ролей без доступа
- **Аудит**: Все мутирующие операции логируются автоматически
- **RBAC**: Используйте `require_roles()` или `require_scopes()` зависимости

## Тестирование

```bash
# Все тесты
pytest

# С покрытием
pytest --cov=app tests/

# Конкретный файл
pytest tests/api/v1/test_objects.py
```

## Миграции БД

```bash
# Создать миграцию
alembic revision --autogenerate -m "add indexes"

# Применить
alembic upgrade head

# Откатить
alembic downgrade -1
```

## Добавление индексов

Добавляйте индексы в `__table_args__` моделей:

```python
__table_args__ = (
    Index("ix_objects_city_id", "city_id"),
    Index("ix_objects_status", "status"),
)
```

**Обязательно** создайте миграцию:

```bash
alembic revision --autogenerate -m "add indexes"
alembic upgrade head
```

Индексы **не создадутся автоматически** без миграции!

