from fastapi import APIRouter
from config.settings import settings
import os

router = APIRouter()

@router.get("/health")
async def health_check():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV
    }
