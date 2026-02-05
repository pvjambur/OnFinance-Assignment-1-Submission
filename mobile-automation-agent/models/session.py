from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class Session(BaseModel):
    id: UUID
    user_id: UUID
    task_id: Optional[UUID] = None
    state: Dict[str, Any]
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class SessionCreate(BaseModel):
    user_id: UUID
    task_id: Optional[UUID] = None
    state: Dict[str, Any]

class SessionUpdate(BaseModel):
    state: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    updated_at: datetime = datetime.now()
