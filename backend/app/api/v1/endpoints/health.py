from fastapi import APIRouter
from app.schemas.health import HealthCheckResponse

router = APIRouter()


@router.get("/health", response_model=HealthCheckResponse, summary="Health Check")
def get_health() -> HealthCheckResponse:
    """
    Returns operational health status of WeatherGPT core backend service.
    """
    return HealthCheckResponse(status="ok", service="WeatherGPT")
