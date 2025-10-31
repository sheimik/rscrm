# Интеграция фронтенда с бэкендом

## Что было реализовано

### 1. API клиент для фронтенда
- Создан `site/src/lib/api.ts` - универсальный API клиент
- Поддержка авторизации через JWT токены
- Методы для работы с объектами, клиентами, визитами, аналитикой и справочниками

### 2. Реализованные эндпоинты бэкенда
- **Визиты**: Полный CRUD (list, create, update, complete) с фильтрацией
- **Словари**: Получение городов и районов из БД

### 3. Замена мок-данных на API
- `Login.tsx` - реальная авторизация через API
- `Dashboard.tsx` - загрузка данных через API с React Query
- `Objects.tsx` - список объектов с фильтрацией через API
- `Visits.tsx` - список визитов через API
- `Customers.tsx` - список клиентов через API

### 4. Скрипт для заполнения БД
- `backend/scripts/seed_test_data.py` - заполнение тестовыми данными:
  - 4 пользователя (admin, supervisor, 2 engineer)
  - 3 объекта
  - 3 клиента
  - 4 визита

## Настройка и запуск

### 1. Заполнение справочников
```bash
cd backend
python scripts/seed_dictionaries.py
```

### 2. Заполнение тестовых данных
```bash
cd backend
python scripts/seed_test_data.py
```

### 3. Настройка переменных окружения

#### Бэкенд
В файле `backend/.env` должен быть установлен:
```
JWT_SECRET=<любая строка длиной >= 32 символов>
DATABASE_URL=sqlite+aiosqlite:///./data/crm.db
CORS_ORIGINS=["http://localhost:8080"]
```

#### Фронтенд
В файле `site/.env` (опционально, по умолчанию используется `http://localhost:8000`):
```
VITE_API_BASE_URL=http://localhost:8000
```

### 4. Запуск бэкенда
```bash
cd backend
python scripts/start_server.py
# Или
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 5. Запуск фронтенда
```bash
cd site
npm install
npm run dev
```

## Учетные данные для тестирования

После запуска `seed_test_data.py`:

- **Admin**: `admin@example.com` / `admin123`
- **Supervisor**: `supervisor@example.com` / `supervisor123`
- **Engineer 1**: `engineer1@example.com` / `engineer123`
- **Engineer 2**: `engineer2@example.com` / `engineer123`

## Тестирование

1. Откройте `http://localhost:8080`
2. Войдите с учетными данными admin
3. Проверьте:
   - Dashboard показывает реальные данные из БД
   - Объекты загружаются через API
   - Визиты загружаются через API
   - Клиенты загружаются через API
   - Создание объекта работает

## Особенности реализации

1. **Авторизация**: JWT токены хранятся в localStorage
2. **React Query**: Используется для кеширования и управления состоянием загрузки
3. **Обработка ошибок**: Показ toast-уведомлений при ошибках API
4. **Маппинг данных**: Конвертация между форматами фронтенда (русские названия) и бэкенда (enum значения)

## Примечания

- CORS настроен для `http://localhost:8080` по умолчанию
- Все даты отображаются в формате локали (ru-RU)
- Статусы и типы конвертируются между русскими и английскими значениями

