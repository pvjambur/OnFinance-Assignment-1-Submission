from fastapi import APIRouter
from models.credential import CredentialCreate
from core.credential_manager import credential_manager

router = APIRouter()

@router.post("/credentials")
async def store_credential(cred: CredentialCreate):
    """
    Securely store a credential.
    """
    success = credential_manager.store_credential(
        user_id=str(cred.user_id),
        app_name=cred.app_name,
        email=cred.email_encrypted, # In real API, receive plain and encrypt here
        password=cred.password_encrypted
    )
    
    if success:
        return {"status": "stored"}
    else:
        return {"status": "failed"}
