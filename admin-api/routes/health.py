from datetime import datetime
from fastapi import APIRouter

from models.health_status_model import HealthStatusModel

health_route = APIRouter(tags=["Health Routes"], prefix="/health")


@health_route.get("/status")
async def get_health() -> HealthStatusModel:
    return HealthStatusModel(status="UP", time=datetime.now())
