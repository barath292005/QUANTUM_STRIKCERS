from fastapi import APIRouter, Query, HTTPException, status
from app.services.weather.schemas import WeatherResponse, ForecastResponse
from app.services.weather.service import WeatherService
from app.services.weather.exceptions import (
    InvalidCoordinatesError,
    ProviderConfigError,
    ProviderTimeoutError,
    ProviderApiError,
    WeatherServiceError,
)

router = APIRouter()
weather_service = WeatherService()


@router.get("/current", response_model=WeatherResponse, summary="Get Real-Time Current Weather")
async def get_current_weather(
    lat: float = Query(..., description="Latitude coordinate (-90.0 to 90.0)"),
    lon: float = Query(..., description="Longitude coordinate (-180.0 to 180.0)"),
) -> WeatherResponse:
    """
    Fetch real-time current weather metrics for latitude/longitude coordinates.
    Data is normalized into WeatherGPT schema from the active weather provider.
    """
    try:
        return await weather_service.get_current_weather(lat, lon)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderConfigError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except WeatherServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/forecast", response_model=ForecastResponse, summary="Get Weather Forecast")
async def get_forecast(
    lat: float = Query(..., description="Latitude coordinate (-90.0 to 90.0)"),
    lon: float = Query(..., description="Longitude coordinate (-180.0 to 180.0)"),
) -> ForecastResponse:
    """
    Fetch 24-hour / multi-day forecast weather metrics for latitude/longitude coordinates.
    """
    try:
        return await weather_service.get_forecast(lat, lon)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderConfigError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except WeatherServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
