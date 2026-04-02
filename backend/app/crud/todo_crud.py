import json
from datetime import datetime, timezone

import redis
from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..config import settings
from ..crud.user_crud import user_streak_management
from ..models import TodoItem
from ..models.user import User
from ..schemas.todo_schemas import TodoItemCreate, TodoItemUpdate

redis_client = redis.Redis(
    host=settings.redis_host,
    port=settings.redis_port,
    db=0,
    decode_responses=True,
)


def create_todo_item(db: Session, todo_data: TodoItemCreate, current_user: User):
    db_todo = TodoItem(user_id=current_user.id, **todo_data.model_dump())
    if db_todo.status == "Completed":
        db_todo.completed_at = datetime.now(settings.tzinfo)
        current_user.tasks_completed = (current_user.tasks_completed or 0) + 1
    db.add(db_todo)
    db.commit()
    db.refresh(db_todo)
    return db_todo


def get_todo_item(db: Session, todo_id: int):
    return db.query(TodoItem).filter(TodoItem.id == todo_id).first()


def get_user_todo_items(db: Session, current_user: User, skip: int = 0, limit: int = 10):
    all_todos = (
        db.query(TodoItem)
        .filter(TodoItem.user_id == current_user.id)
        .order_by(TodoItem.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return all_todos


def get_completed_tasks(db: Session, current_user: User, skip: int = 0, limit: int = 10):
    completed_todos = (
        db.query(TodoItem)
        .filter(TodoItem.user_id == current_user.id, TodoItem.status == "Completed")
        .order_by(TodoItem.updated_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return completed_todos


def update_todo_item(db: Session, todo_id: int, todo_data: TodoItemUpdate, current_user: User):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()

    if not todo:
        return None

    for key, value in todo_data.model_dump(exclude_unset=True).items():
        setattr(todo, key, value)

    if todo.status == "Completed" and todo.completed_at is None:
        todo.completed_at = datetime.now(settings.tzinfo)
        current_user.tasks_completed = (current_user.tasks_completed or 0) + 1

    db.commit()
    db.refresh(todo)
    return todo


def delete_todo_item(db: Session, todo_id: int, current_user: User):
    db_todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if db_todo:
        redis_client.delete(f"pomodoro:{current_user.id}:{todo_id}")
        db.delete(db_todo)
        db.commit()
    return db_todo


def start_pomodoro(db: Session, todo_id: int, current_user: User):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    key = f"pomodoro:{current_user.id}:{todo_id}"
    session_data = redis_client.get(key)

    start_time = datetime.now(timezone.utc).isoformat()
    accumulated_time = 0

    if session_data:
        session = json.loads(session_data)
        accumulated_time = session.get("accumulated_time", 0)

    redis_client.set(key, json.dumps({"start_time": start_time, "accumulated_time": accumulated_time}), ex=60 * 120)

    return {
        "message": "Pomodoro started",
        "start_time": start_time,
        "accumulated_time": int(accumulated_time),
    }


def pause_pomodoro(db: Session, todo_id: int, current_user: User):
    key = f"pomodoro:{current_user.id}:{todo_id}"
    session_data = redis_client.get(key)
    if not session_data:
        raise HTTPException(status_code=400, detail="No active pomodoro session for this task")

    session = json.loads(session_data)
    start_time = session.get("start_time")
    elapsed_time = 0
    if start_time:
        elapsed_time = (
            datetime.now(timezone.utc) - datetime.fromisoformat(start_time)
        ).total_seconds()

    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    accumulated_time = session.get("accumulated_time", 0) + elapsed_time

    redis_client.set(key, json.dumps({"accumulated_time": accumulated_time}), ex=60 * 120)

    db.commit()
    db.refresh(todo)
    return {"message": "Pomodoro paused", "elapsed_time": int(accumulated_time)}


def finish_pomodoro(db: Session, todo_id: int, current_user: User):
    key = f"pomodoro:{current_user.id}:{todo_id}"
    session_data = redis_client.get(key)
    if not session_data:
        raise HTTPException(status_code=400, detail="No active pomodoro session for this task")

    session = json.loads(session_data)
    start_time = session.get("start_time")
    elapsed_time = 0
    if start_time:
        elapsed_time = (
            datetime.now(timezone.utc) - datetime.fromisoformat(start_time)
        ).total_seconds()

    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    accumulated_time = session.get("accumulated_time", 0) + elapsed_time

    todo.total_time_spent = (todo.total_time_spent or 0) + int(accumulated_time)
    todo.pomodoro_sessions = (todo.pomodoro_sessions or 0) + 1
    current_user.pomodoro_sessions = (current_user.pomodoro_sessions or 0) + 1

    redis_client.delete(key)
    db.commit()
    db.refresh(todo)
    return {
        "message": "Pomodoro finished",
        "elapsed_time": int(accumulated_time),
        "total_pomodoros": todo.pomodoro_sessions,
    }


def get_pomodoro(db: Session, todo_id: int, current_user: User):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    key = f"pomodoro:{current_user.id}:{todo_id}"
    session_data = redis_client.get(key)

    if not session_data:
        return {"elapsed_time": 0, "is_running": False, "accumulated_time": 0, "started_at": None}

    session = json.loads(session_data)
    if "start_time" in session:
        elapsed_time = (datetime.now(timezone.utc) - datetime.fromisoformat(session["start_time"])).total_seconds()
        accumulated_time = session.get("accumulated_time", 0)
        return {
            "elapsed_time": int(accumulated_time + elapsed_time),
            "is_running": True,
            "accumulated_time": int(accumulated_time),
            "started_at": session["start_time"],
        }

    accumulated_time = session.get("accumulated_time", 0)
    return {
        "elapsed_time": int(accumulated_time),
        "is_running": False,
        "accumulated_time": int(accumulated_time),
        "started_at": None,
    }


def mark_task_as_completed(db: Session, todo_id: int, current_user: User):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    if todo.completed_at:
        raise HTTPException(status_code=400, detail="Task is already completed")

    todo.status = "Completed"
    current_user.tasks_completed = (current_user.tasks_completed or 0) + 1
    todo.completed_at = datetime.now(settings.tzinfo)
    db.commit()
    db.refresh(todo)
    return todo


def todo_streak_management(db: Session, todo_id: int, current_user: User):
    todo = db.query(TodoItem).filter(TodoItem.id == todo_id, TodoItem.user_id == current_user.id).first()
    if not todo:
        raise HTTPException(status_code=404, detail="Todo not found")

    today = datetime.now(settings.tzinfo).date()

    if todo.current_streak is None or todo.last_activity_date is None or todo.longest_streak is None:
        todo.current_streak = 1
        todo.longest_streak = 1
        todo.last_activity_date = today
    else:
        if (today - todo.last_activity_date).days == 1:
            todo.current_streak += 1
            todo.last_activity_date = today
            if todo.current_streak > todo.longest_streak:
                todo.longest_streak = todo.current_streak
        elif (today - todo.last_activity_date).days > 1:
            todo.current_streak = 1
            todo.last_activity_date = today
        else:
            return {"message": "Streak already updated for today",
                    "current_streak": todo.current_streak,
                    "longest_streak": todo.longest_streak
                    }

    db.commit()
    db.refresh(todo)

    user_streak_management(current_user.id, db)

    return {"message": "Streak updated",
            "current_streak": todo.current_streak,
            "longest_streak": todo.longest_streak
            }
