"""
Weather Engine Domain Package for WeatherGPT.
Integrates real-time weather providers, normalizes telemetry data, and caches responses.
"""

from app.services.weather.service import WeatherService
from app.services.weather.provider import BaseWeatherProvider
from app.services.weather.schemas import (
    Location,
    CurrentWeather,
    ForecastItem,
    WeatherResponse,
    ForecastResponse,
)
from app.services.weather.exceptions import (
    WeatherServiceError,
    InvalidCoordinatesError,
    ProviderConfigError,
    ProviderTimeoutError,
    ProviderApiError,
)

__all__ = [
    "WeatherService",
    "BaseWeatherProvider",
    "Location",
    "CurrentWeather",
    "ForecastItem",
    "WeatherResponse",
    "ForecastResponse",
    "WeatherServiceError",
    "InvalidCoordinatesError",
    "ProviderConfigError",
    "ProviderTimeoutError",
    "ProviderApiError",
]
