from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from ..crud.todo_crud import (
    create_todo_item,
    get_todo_item,
    get_user_todo_items,
    update_todo_item,
    delete_todo_item,
    start_pomodoro,
    pause_pomodoro,
    finish_pomodoro,
    mark_task_as_completed,
    get_completed_tasks,
    get_pomodoro,
    todo_streak_management
)
from ..crud.user_crud import get_current_user
from ..db.session import get_db
from ..models.user import User
from ..schemas.todo_schemas import (
    PomodoroFinishResponse,
    PomodoroPauseResponse,
    PomodoroStartResponse,
    PomodoroStateResponse,
    StreakResponse,
    TodoCompleteResponse,
    TodoItemCreate,
    TodoItemUpdate,
    TodoItemResponse,
    TodoWithStreak
)

router = APIRouter()


@router.post("/todos/", response_model=TodoWithStreak)
def create_task(todo: TodoItemCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo_item = create_todo_item(db, todo, current_user)
    streak_update = todo_streak_management(db, todo_item.id, current_user)
    return {"todo": todo_item, "streak": streak_update}


@router.get("/todos/{todo_id}", response_model=TodoItemResponse)
def read_task(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = get_todo_item(db, todo_id)
    if not todo or todo.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Todo not found")
    return todo


@router.get("/todos/all/", response_model=list[TodoItemResponse])
def read_user_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                    current_user: User = Depends(get_current_user)):
    return get_user_todo_items(db, current_user, skip, limit)


@router.get("/todos/completed/", response_model=list[TodoItemResponse])
def read_user_completed_tasks(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),
                              current_user: User = Depends(get_current_user)):
    return get_completed_tasks(db, current_user, skip, limit)


@router.put("/todos/{todo_id}", response_model=TodoItemResponse)
def update_task(todo_id: int, todo: TodoItemUpdate, db: Session = Depends(get_db),
                current_user: User = Depends(get_current_user)):
    updated_task = update_todo_item(db, todo_id, todo, current_user)
    if not updated_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return updated_task


@router.delete("/todos/{todo_id}")
def delete_task(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    deleted_task = delete_todo_item(db, todo_id, current_user)
    if not deleted_task:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"message": "Task deleted"}


@router.post("/todos/{todo_id}/complete", response_model=TodoCompleteResponse)
def complete_task(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    todo = mark_task_as_completed(db, todo_id, current_user)
    streak_result = todo_streak_management(db, todo_id, current_user)
    return {"todo": todo, "streak": streak_result}


@router.post("/todos/{todo_id}/pomodoro/start", response_model=PomodoroStartResponse)
def start_pomodoro_timer(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return start_pomodoro(db, todo_id, current_user)


@router.post("/todos/{todo_id}/pomodoro/pause", response_model=PomodoroPauseResponse)
def pause_pomodoro_timer(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return pause_pomodoro(db, todo_id, current_user)


@router.post("/todos/{todo_id}/pomodoro/finish", response_model=PomodoroFinishResponse)
def finish_pomodoro_timer(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    pomodoro_result = finish_pomodoro(db, todo_id, current_user)
    streak_result = todo_streak_management(db, todo_id, current_user)
    return {"pomodoro": pomodoro_result, "streak": streak_result}


@router.get("/todos/{todo_id}/pomodoro/status", response_model=PomodoroStateResponse)
def get_pomodoro_status(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return get_pomodoro(db, todo_id, current_user)


@router.put("/todos/{todo_id}/streak/", response_model=StreakResponse)
def update_todo_streak(todo_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return todo_streak_management(db=db, todo_id=todo_id, current_user=current_user)
