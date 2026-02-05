from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, ConfigDict
from enum import Enum

class TaskStatus(str, Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"

class TaskHistory(BaseModel):
    id: UUID
    user_id: UUID
    command: str
    intent: Optional[Dict[str, Any]] = None
    app_name: Optional[str] = None
    status: TaskStatus
    steps: List[Dict[str, Any]] = []
    result: Optional[str] = None
    error: Optional[str] = None
    duration_seconds: Optional[int] = None
    started_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class TaskCreate(BaseModel):
    user_id: UUID
    command: str
    status: TaskStatus = TaskStatus.PENDING
    started_at: datetime = datetime.now()

class TaskUpdate(BaseModel):
    status: Optional[TaskStatus] = None
    steps: Optional[List[Dict[str, Any]]] = None
    result: Optional[str] = None
    error: Optional[str] = None
    completed_at: Optional[datetime] = None
    duration_seconds: Optional[int] = None
