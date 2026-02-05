from datetime import datetime
from uuid import UUID
from typing import Optional, Dict, Any
from pydantic import BaseModel, ConfigDict

class Credential(BaseModel):
    id: UUID
    user_id: UUID
    app_name: str
    app_package: Optional[str] = None
    email_encrypted: str
    password_encrypted: str
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class CredentialCreate(BaseModel):
    user_id: UUID
    app_name: str
    app_package: Optional[str] = None
    email_encrypted: str
    password_encrypted: str
    metadata: Optional[Dict[str, Any]] = {}
