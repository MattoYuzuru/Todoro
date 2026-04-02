# Todoly

Небольшой full-stack todo-сервис на FastAPI и Vue 3. Приложение умеет:

- регистрировать и авторизовывать пользователей по JWT;
- создавать, редактировать и удалять задачи;
- отмечать выполнение задач;
- запускать Pomodoro по задаче с хранением состояния в Redis;
- считать streak и базовую пользовательскую статистику;
- показывать задачи по датам в календарном представлении.

## Стек

- Backend: FastAPI, SQLAlchemy, Alembic, Redis
- Frontend: Vue 3, Vue Router, Pinia, Vite
- Infrastructure: Docker Compose, PostgreSQL

## Быстрый старт

1. Скопируйте шаблоны окружения:

```bash
cp .env.example .env
cp .env_db.example .env_db
```

2. Сгенерируйте `SECRET_KEY`:

```bash
openssl rand -hex 32
```

3. Поднимите проект:

```bash
docker compose up -d --build
```

4. Откройте:

- Frontend: `http://localhost:8080`
- Backend API: `http://localhost:8000`
- Swagger UI: `http://localhost:8000/docs`

## Переменные окружения

`.env`:

```env
DATABASE_URL=postgresql+psycopg2://todo_user:change_me@postgres:5432/todo_db
SECRET_KEY=replace_with_generated_secret
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
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

## Что важно знать

- Миграции Alembic применяются автоматически при старте backend-контейнера.
- `.env` и `.env_db` не должны попадать в git; используйте только `.env.example` и `.env_db.example`.
- Для локальной разработки без Docker backend читает настройки из переменных окружения или `.env`.

## Проверка качества

Базовая проверка:

```bash
docker compose up -d --build
docker compose exec -T backend pytest -q
docker compose exec -T frontend npm run build
docker compose down
```
