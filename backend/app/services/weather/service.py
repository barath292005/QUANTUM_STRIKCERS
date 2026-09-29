from typing import Optional
from app.core.config import settings
from app.services.weather.provider import BaseWeatherProvider
from app.services.weather.providers.openmeteo import OpenMeteoProvider
from app.services.weather.providers.openweather import OpenWeatherProvider
from app.services.weather.schemas import WeatherResponse, ForecastResponse
from app.services.weather.cache import weather_cache
from app.services.weather.exceptions import InvalidCoordinatesError


class WeatherService:
    """
    Main Weather Domain Service.
    Orchestrates provider selection, coordinate validation, and caching.
    """

    def __init__(self, provider: Optional[BaseWeatherProvider] = None):
        if provider:
            self.provider = provider
        else:
            provider_type = settings.WEATHER_PROVIDER.lower()
            if provider_type == "openweather":
                self.provider = OpenWeatherProvider(api_key=settings.OPENWEATHER_API_KEY)
            else:
                self.provider = OpenMeteoProvider(base_url=settings.OPEN_METEO_BASE_URL)

    def _validate_coordinates(self, lat: float, lon: float) -> None:
        if not (-90.0 <= lat <= 90.0):
            raise InvalidCoordinatesError(f"Invalid latitude {lat}. Latitude must be between -90 and 90 degrees.")
        if not (-180.0 <= lon <= 180.0):
            raise InvalidCoordinatesError(f"Invalid longitude {lon}. Longitude must be between -180 and 180 degrees.")

    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        self._validate_coordinates(lat, lon)
        cached = weather_cache.get("current", lat, lon)
        if cached:
            return cached

        response = await self.provider.get_current_weather(lat, lon)
        weather_cache.set("current", lat, lon, response, ttl=settings.WEATHER_CACHE_TTL_SECONDS)
        return response

    async def get_forecast(self, lat: float, lon: float) -> ForecastResponse:
        self._validate_coordinates(lat, lon)
        cached = weather_cache.get("forecast", lat, lon)
        if cached:
            return cached

        response = await self.provider.get_forecast(lat, lon)
        weather_cache.set("forecast", lat, lon, response, ttl=settings.WEATHER_CACHE_TTL_SECONDS)
        return response
