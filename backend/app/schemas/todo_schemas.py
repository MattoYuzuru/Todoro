from datetime import date, datetime
from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

TodoStatus = Literal["Pending", "Postponed", "In Progress", "Completed"]
TodoPriority = Literal["Low", "Medium", "High"] | None


class TodoItemBase(BaseModel):
    title: str = Field(..., max_length=100)
    description: Optional[str] = None
    status: TodoStatus = "Pending"
    priority: TodoPriority = None
    due_date: Optional[date] = None


class TodoItemCreate(TodoItemBase):
    pass


class TodoItemUpdate(BaseModel):
    title: Optional[str] = Field(default=None, max_length=100)
    description: Optional[str] = None
    status: Optional[TodoStatus] = None
    priority: TodoPriority = None
    due_date: Optional[date] = None


class TodoItemResponse(TodoItemBase):
    id: int
    user_id: int
    collaborators: list[int] = Field(default_factory=list)
    pomodoro_sessions: int = 0
    total_time_spent: int = 0
    current_streak: int = 0
    longest_streak: int = 0
    last_activity_date: Optional[date] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class StreakResponse(BaseModel):
    message: str
    current_streak: int
    longest_streak: int


class TodoWithStreak(BaseModel):
    todo: TodoItemResponse
    streak: StreakResponse


class TodoCompleteResponse(BaseModel):
    todo: TodoItemResponse
    streak: StreakResponse


class PomodoroStartResponse(BaseModel):
    message: str
    start_time: str
    accumulated_time: int


class PomodoroPauseResponse(BaseModel):
    message: str
    elapsed_time: int


class PomodoroStateResponse(BaseModel):
    elapsed_time: int
    is_running: bool
    accumulated_time: int
    started_at: Optional[str] = None


class PomodoroFinishPayload(BaseModel):
    message: str
    elapsed_time: int
    total_pomodoros: int


class PomodoroFinishResponse(BaseModel):
    pomodoro: PomodoroFinishPayload
    streak: StreakResponse
