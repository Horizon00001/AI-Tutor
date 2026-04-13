from fastapi import APIRouter
from datetime import datetime

from api.models.schemas import HealthResponse

router = APIRouter(prefix="/health", tags=["健康检查"])

@router.get("", response_model=HealthResponse)
async def health_check():
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now()
    )

@router.get("/ready")
async def readiness_check():
    return {
        "status": "ready",
        "timestamp": datetime.now().isoformat()
    }
