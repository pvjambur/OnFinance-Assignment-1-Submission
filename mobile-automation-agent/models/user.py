from datetime import datetime
from uuid import UUID
from typing import Optional
from pydantic import BaseModel, EmailStr, ConfigDict

class User(BaseModel):
    id: UUID
    email: EmailStr
    pin_hash: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserCreate(BaseModel):
    email: EmailStr
    pin_hash: str

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    pin_hash: Optional[str] = None
