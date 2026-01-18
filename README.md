# AI Prelanding Copy Engine

Система для генерации высококонверсионного prelanding-контента на основе библиотеки успешных реальных примеров с использованием AI.

## Возможности

- 🤖 **Multimodal AI**: GPT-4o Vision для анализа текста и визуальных элементов
- 📊 **Performance-Driven**: Обучение на реальных метриках конверсии
- 🎯 **Compliance Layer**: Автоматическая проверка на соответствие требованиям рекламных сетей
- 🔄 **Active Learning**: Система самообучения на основе обратной связи
- 🌍 **Multi-GEO**: Поддержка различных географических регионов и языков
- 🎨 **Persona-Based**: Генерация с различными стилями (агрессивный, скептический, восторженный)

## Технологический стек

### Backend

- **FastAPI** - Modern async Python framework
- **PostgreSQL** - Relational database
- **Qdrant** - Vector database для RAG
- **OpenAI GPT-4o** - Multimodal LLM
- **LangChain** - RAG orchestration

### Frontend

- **Next.js 14** - React framework с App Router
- **TypeScript** - Type safety
- **TailwindCSS** - Styling
- **shadcn/ui** - Component library

## Быстрый старт

### Требования

- Docker и Docker Compose
- OpenAI API key с доступом к GPT-4o

### Установка

1. Клонируйте репозиторий:

```bash
git clone <repository-url>
cd lending_base
```

1. Создайте `.env` файл:

```bash
cp .env.example .env
```

1. Добавьте ваш OpenAI API key в `.env`:

```
OPENAI_API_KEY=sk-your-actual-key-here
```

1. Запустите сервисы:

```bash
docker-compose up -d
```

1. Примените миграции базы данных:

```bash
docker-compose exec backend alembic upgrade head
```

1. Откройте приложение:

- Frontend: <http://localhost:3000>
- Backend API: <http://localhost:8000>
- API Docs: <http://localhost:8000/docs>

## Использование

### 1. Загрузка Prelandings

Перейдите в Library и загрузите архив prelanding'а:

- `index.html` - основной файл
- `screenshots/` - скриншоты страницы
- `meta.json` - метаданные и метрики

### 2. Генерация нового контента

1. Перейдите в **Generate**
2. Выберите параметры:
   - GEO (страна)
   - Язык
   - Вертикаль (crypto, finance, etc.)
   - Offer
   - Persona (стиль написания)
   - Compliance level
3. Нажмите **Generate**
4. Экспортируйте результат в нужном формате

### 3. Отправка обратной связи

Через API можно отправлять метрики производительности:

```bash
curl -X POST http://localhost:8000/api/feedback \
  -H "Content-Type: application/json" \
  -d '{
    "gen_id": "generated_prelanding_id",
    "lead_rate": 8.5,
    "ctr_to_landing": 15.2,
    "deposit_rate": 3.1
  }'
```

При `lead_rate > 5%` система автоматически добавит сгенерированный prelanding в библиотеку источников.

## Структура проекта

```
lending_base/
├── backend/
│   ├── app/
│   │   ├── models/         # SQLAlchemy models
│   │   ├── routes/         # API endpoints
│   │   ├── services/       # Business logic
│   │   └── main.py         # FastAPI app
│   ├── alembic/            # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── app/                # Next.js pages
│   ├── components/         # React components
│   └── package.json
└── docker-compose.yml
```

## API Endpoints

### Prelandings

- `POST /api/prelandings/upload` - Загрузка нового prelanding
- `GET /api/prelandings` - Список с фильтрами
- `GET /api/prelandings/{id}` - Детали prelanding
- `GET /api/prelandings/top` - Топ performers

### Generation

- `POST /api/generate` - Генерация нового копирайта
- `GET /api/generate/{gen_id}` - Получить результат
- `POST /api/generate/{gen_id}/export` - Экспорт в форматах

### Feedback

- `POST /api/feedback` - Отправка метрик

## Разработка

### Backend Development

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Frontend Development

```bash
cd frontend
npm install
npm run dev
```

### Тестирование

```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## Лицензия

MIT License

## Контакты

For questions and support, please open an issue.
