#!/bin/sh
set -e

python - <<'PY'
import os
import time

from sqlalchemy import create_engine, text

database_url = os.environ["DATABASE_URL"]

for attempt in range(30):
    try:
        engine = create_engine(database_url, pool_pre_ping=True)
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        print("Database connection established.")
        break
    except Exception as exc:  # noqa: BLE001
        print(f"Waiting for database ({attempt + 1}/30): {exc}")
        time.sleep(2)
else:
    raise SystemExit("Database is unavailable after waiting.")
PY

alembic -c /app/alembic.ini upgrade head

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
