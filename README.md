# Todoro

Todoro — это full-stack сервис для управления задачами, фокус-сессиями и личной продуктивностью.

Что умеет проект:
- регистрация и вход по JWT;
- создание, редактирование, удаление и завершение задач;
- Pomodoro-таймеры по задачам с хранением состояния в Redis;
- календарное представление по дедлайнам;
- дашборд со сводками, графиками и базовой аналитикой;
- профиль пользователя со streak-метриками и настройками аккаунта.

## Стек

- Backend: FastAPI, SQLAlchemy, Alembic, Redis
- Frontend: Vue 3, Vue Router, Pinia, Vite
- Infrastructure: Docker Compose, PostgreSQL

## Быстрый старт

1. Создай локальные env-файлы из шаблонов:

```bash
cp .env.example .env
cp .env_db.example .env_db
```

2. Сгенерируй новый `SECRET_KEY`:

```bash
openssl rand -hex 32
```

3. Запусти проект:

```bash
docker compose up -d --build
```

4. Открой сервисы:

- фронтенд: `http://localhost:8080`
- backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

Если раньше уже поднимался старый Postgres volume с другими кредами, сбрось его один раз:

```bash
docker compose down -v
docker compose up -d --build
```

## Основные переменные окружения

`.env`:

```env
DATABASE_URL=postgresql+psycopg2://todo_user:change_me@postgres:5432/todo_db
SECRET_KEY=replace_with_generated_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=4320
TIME_ZONE=Europe/Moscow
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:8080,http://127.0.0.1:8080
REDIS_HOST=redis
REDIS_PORT=6379
VITE_API_BASE_URL=http://localhost:8000
```

`.env_db`:

```env
POSTGRES_USER=todo_user
POSTGRES_PASSWORD=change_me
POSTGRES_DB=todo_db
```

`ACCESS_TOKEN_EXPIRE_MINUTES=4320` — это 3 дня жизни JWT-токена.

## Как устроен запуск

- backend при старте ждет доступность базы данных;
- затем автоматически применяет миграции Alembic;
- после этого стартует Uvicorn;
- frontend собирается через Vite и раздается контейнером на `8080`.

## Проверка после изменений

Базовый набор команд:

```bash
docker compose up -d --build
docker compose exec -T backend pytest -q
docker compose exec -T frontend npm run build
docker compose down
```

## Важно

- `.env` и `.env_db` не должны попадать в Git.
- Для репозитория используются `.env.example` и `.env_db.example`.
- Если меняешь зависимости или Docker-образы, перепроверь `docker compose up -d --build`.
