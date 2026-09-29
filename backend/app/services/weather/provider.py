from abc import ABC, abstractmethod
from app.services.weather.schemas import WeatherResponse, ForecastResponse


class BaseWeatherProvider(ABC):
    """
    Abstract Provider Interface for external weather data services.
    Every provider must normalize raw responses into WeatherGPT schemas.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Returns string identifier for the weather provider."""
        pass

    @abstractmethod
    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        """Retrieves and normalizes real-time current weather metrics for given coordinates."""
        pass

    @abstractmethod
    async def get_forecast(self, lat: float, lon: float) -> ForecastResponse:
        """Retrieves and normalizes forecast weather metrics for given coordinates."""
        pass
