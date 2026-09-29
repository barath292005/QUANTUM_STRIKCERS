from fastapi import APIRouter
from app.api.v1.endpoints import health, weather, climate, risk

api_router = APIRouter()
api_router.include_router(health.router, tags=["Health"])
api_router.include_router(weather.router, prefix="/weather", tags=["Weather Engine"])
api_router.include_router(climate.router, prefix="/climate", tags=["Climate Engine"])
api_router.include_router(risk.router, prefix="/risk", tags=["Risk Engine"])
