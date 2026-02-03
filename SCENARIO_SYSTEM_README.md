# Система Сценариев и Генераторов - Руководство по запуску

## Обзор изменений

Добавлена система трёхчастной генерации прелендингов на основе сценариев:
- ✅ 4 готовых сценария (расследование, ток-шоу, отменённое интервью, интервью изданию)
- ✅ Генератор имён для разных стран и полов
- ✅ Генератор отзывов с поддержкой языков
- ✅ UI для управления сценариями
- ✅ Страница генераторов

## Изменённые/Новые файлы

### Backend (Python/FastAPI)

**Модели:**
- `backend/app/models/scenario.py` - новая модель Scenario
- `backend/app/models/prelanding.py` - обновлена GeneratedPrelanding (добавлены поля scenario_id, beginning_text, middle_text, end_text)

**Сервисы:**
- `backend/app/services/scenario_manager.py` - CRUD для сценариев
- `backend/app/services/name_generator.py` - генерация имён через Claude API
- `backend/app/services/review_generator.py` - генерация отзывов через Claude API
- `backend/app/services/copy_generator.py` - обновлён, добавлен метод `generate_with_scenario`

**API Routes:**
- `backend/app/routes/scenarios.py` - эндпоинты для работы со сценариями
- `backend/app/routes/generators.py` - эндпоинты для генераторов имён и отзывов
- `backend/app/routes/generation.py` - обновлён, добавлен `/with-scenario`

**Прочее:**
- `backend/app/schemas.py` - добавлены новые Pydantic схемы
- `backend/app/config.py` - добавлен `anthropic_api_key`
- `backend/app/main.py` - подключены новые роуты
- `backend/app/seeds/initial_scenarios.py` - начальные данные (4 сценария)
- `backend/init_db.py` - скрипт инициализации БД

### Frontend (Next.js/TypeScript)

**Компоненты:**
- `frontend/app/components/ScenarioManager.tsx` - модальное окно управления сценариями
- `frontend/app/components/Header.tsx` - обновлена навигация

**Страницы:**
- `frontend/app/generate/page.tsx` - обновлена форма генерации (добавлен выбор сценария)
- `frontend/app/generators/page.tsx` - новая страница с генераторами имён и отзывов

## Инструкции по запуску

### 1. Backend

#### Установка зависимостей

Все необходимые зависимости уже установлены (используется OpenAI API, который уже подключён).

#### Настройка переменных окружения

Убедитесь, что в `backend/.env` есть OpenAI API ключ:
```bash
OPENAI_API_KEY=your_openai_key_here
```

**ВАЖНО:** Генераторы имён и отзывов используют тот же OpenAI API ключ, что и основная генерация прелендингов.

#### Инициализация БД

Создайте таблицы и добавьте начальные сценарии:
```bash
cd backend
python init_db.py
```

Должен вывести:
```
Creating database tables...
✓ Tables created successfully

Seeding initial data...
Created scenario: Статья-расследование
Created scenario: Интервью на ток-шоу
Created scenario: Отменённое интервью на ток-шоу
Created scenario: Интервью новостному изданию

Seeded 4 scenarios successfully

✓ Database initialization completed!
```

#### Запуск backend

```bash
cd backend
uvicorn app.main:app --reload
```

API будет доступен на http://localhost:8000

### 2. Frontend

#### Установка зависимостей

Зависимости должны быть уже установлены (используются существующие библиотеки).

#### Запуск frontend

```bash
cd frontend
npm run dev
```

Frontend будет доступен на http://localhost:3000

## Использование

### 1. Генерация со сценарием

1. Перейдите на http://localhost:3000/generate
2. Заполните форму (GEO, язык, оффер и т.д.)
3. **Выберите сценарий** из выпадающего списка (или оставьте "Без сценария" для обычной генерации)
4. Нажмите "Сгенерировать копирайт"
5. Результат покажется в 3 секциях:
   - **Начало** (700-1000 символов)
   - **Середина** (основной сценарий)
   - **Конец** (доказательства + отзывы)
   - **Полный текст** (всё вместе)

### 2. Управление сценариями

1. На странице генерации нажмите кнопку "Управление" рядом с выбором сценария
2. Откроется модальное окно со списком сценариев
3. Можно:
   - **Создать** новый сценарий с кастомными промптами
   - **Редактировать** существующие сценарии
   - **Удалить** (деактивировать) сценарии

### 3. Генераторы имён и отзывов

1. Перейдите на http://localhost:3000/generators
2. **Генератор имён:**
   - Выберите страну
   - Выберите пол (мужской/женский/случайный)
   - Укажите количество
   - Включите/выключите никнеймы
   - Нажмите "Сгенерировать имена"
3. **Генератор отзывов:**
   - Выберите страну и язык
   - Выберите вертикаль
   - Выберите длину отзыва
   - Укажите количество
   - Нажмите "Сгенерировать отзывы"

## API Endpoints

### Сценарии

- `GET /api/scenarios` - получить список активных сценариев
- `GET /api/scenarios/{id}` - получить сценарий по ID
- `POST /api/scenarios` - создать новый сценарий
- `PUT /api/scenarios/{id}` - обновить сценарий
- `DELETE /api/scenarios/{id}` - деактивировать сценарий

### Генераторы

- `POST /api/generators/names` - сгенерировать имена
  ```json
  {
    "geo": "RU",
    "gender": "random",
    "count": 10,
    "include_nickname": true
  }
  ```

- `POST /api/generators/reviews` - сгенерировать отзывы
  ```json
  {
    "geo": "RU",
    "language": "ru",
    "vertical": "crypto",
    "length": "medium",
    "count": 5
  }
  ```

### Генерация

- `POST /api/generate/with-scenario` - генерация со сценарием
  ```json
  {
    "scenario_id": 1,
    "geo": "RU",
    "language": "ru",
    "vertical": "crypto",
    "offer": "AI Trading Platform",
    "persona": "aggressive_investigator",
    "compliance_level": "strict_facebook",
    "use_rag": true
  }
  ```

## Структура сценария

Каждый сценарий состоит из 3 шаблонов промптов:

1. **beginning_template** - промпт для генерации начала (700-1000 символов)
   - Тизер, который зацепит читателя
   - Интрига, заголовок

2. **middle_template** - промпт для генерации середины (основной сценарий)
   - Развёрнутое повествование по выбранному сценарию
   - 2000-3000 слов

3. **end_template** - промпт для генерации конца (доказательства + отзывы)
   - Социальные доказательства
   - Отзывы реальных людей
   - Описания скриншотов
   - Призыв к действию

## 4 готовых сценария

1. **Статья-расследование** - журналистское расследование о секрете обогащения
2. **Интервью на ток-шоу** - гость раскрывает метод в прямом эфире, конфликт с продюсерами
3. **Отменённое интервью** - "запрещённое" интервью, которое не вышло в эфир
4. **Интервью изданию** - классическое интервью в формате вопрос-ответ

## Проверка работы

### Проверка БД

```python
# backend/check_scenarios.py
from app.database import SessionLocal
from app.models.scenario import Scenario

db = SessionLocal()
scenarios = db.query(Scenario).all()
for s in scenarios:
    print(f"#{s.id} - {s.name_ru}")
db.close()
```

### Проверка API

```bash
# Список сценариев
curl http://localhost:8000/api/scenarios

# Генерация имён
curl -X POST http://localhost:8000/api/generators/names \
  -H "Content-Type: application/json" \
  -d '{"geo":"RU","gender":"random","count":5}'

# Генерация отзывов
curl -X POST http://localhost:8000/api/generators/reviews \
  -H "Content-Type: application/json" \
  -d '{"geo":"RU","language":"ru","vertical":"crypto","length":"medium","count":3}'
```

## Troubleshooting

### Ошибка "OpenAI API key not configured"

**Причина:** Не установлен `OPENAI_API_KEY` в `.env`

**Решение:**
1. Проверьте, что в `backend/.env` есть ключ:
   ```
   OPENAI_API_KEY=sk-...
   ```
2. Перезапустите backend

### Ошибка "Scenario not found"

**Причина:** База данных не инициализирована или сценарии не добавлены

**Решение:**
```bash
cd backend
python init_db.py
```

### Frontend не подключается к backend

**Причина:** Неправильный `NEXT_PUBLIC_API_URL`

**Решение:** Проверьте `frontend/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Генераторы работают медленно

**Причина:** OpenAI API может занимать 5-10 секунд на запрос (особенно для больших объёмов)

**Решение:** Это нормально, GPT-4o генерирует качественный контент

## Дополнительная информация

### Кастомные сценарии

Вы можете создать свои сценарии через UI или напрямую через API:

```python
# Пример создания кастомного сценария
scenario_data = {
    "name": "custom_scenario",
    "name_ru": "Мой сценарий",
    "description": "Описание сценария",
    "beginning_template": "Промпт для начала...",
    "middle_template": "Промпт для середины...",
    "end_template": "Промпт для конца...",
    "order_index": 5
}

response = requests.post(
    "http://localhost:8000/api/scenarios",
    json=scenario_data
)
```

### Расширение системы

Для добавления новых функций:
1. Генераторы других типов контента - создайте новый сервис в `backend/app/services/`
2. Новые типы сценариев - добавьте через UI или seeds
3. Интеграция с изображениями - используйте описания из генераторов для DALL-E/Midjourney

## Контакты

При возникновении проблем создайте issue в репозитории проекта.

---

**Версия:** 1.0.0
**Дата:** 2026-02-03
