from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

try:
    from app.crud.user_crud import get_current_user
    from app.db.session import get_db
    from app.main import app
    from app.routes import todo_router, user_router
except ImportError:
    from backend.app.crud.user_crud import get_current_user
    from backend.app.db.session import get_db
    from backend.app.main import app
    from backend.app.routes import todo_router, user_router


class DummyUser:
    id = 1
    username = "tester"
    email = "tester@example.com"
    current_streak = 2
    longest_streak = 5
    last_activity_date = None
    pomodoro_sessions = 3
    tasks_completed = 7
    created_at = datetime(2026, 1, 1)
    updated_at = datetime(2026, 1, 1)


@contextmanager
def override_dependencies():
    def override_db():
        yield object()

    app.dependency_overrides[get_db] = override_db
    app.dependency_overrides[get_current_user] = lambda: DummyUser()
    try:
        yield
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_healthcheck(client):
    response = client.get("/healthz")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_users_list_requires_auth(client):
    response = client.get("/users/")

    assert response.status_code == 401


def test_users_list_returns_only_current_user(client):
    with override_dependencies():
        response = client.get("/users/")

    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 1
    assert payload[0]["username"] == "tester"


def test_create_user_returns_validation_error_for_duplicate_email(client, monkeypatch):
    def fail_create_user(_db, _payload):
        raise ValueError("This email already exists")

    monkeypatch.setattr(user_router, "create_user", fail_create_user)

    with override_dependencies():
        response = client.post(
            "/create",
            json={
                "username": "tester",
                "email": "tester@example.com",
                "password": "secret123",
            },
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "This email already exists"


def test_streak_endpoint_returns_schema_instead_of_500(client, monkeypatch):
    monkeypatch.setattr(
        todo_router,
        "todo_streak_management",
        lambda db, todo_id, current_user: {
            "message": "Streak updated",
            "current_streak": 3,
            "longest_streak": 5,
        },
    )

    with override_dependencies():
        response = client.put("/todos/10/streak/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "Streak updated",
        "current_streak": 3,
        "longest_streak": 5,
    }
