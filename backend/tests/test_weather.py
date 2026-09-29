import asyncio
import pytest
from unittest.mock import patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.weather.providers.openweather import OpenWeatherProvider
from app.services.weather.schemas import (
    Location,
    CurrentWeather,
    WeatherResponse,
    ForecastItem,
    ForecastResponse,
)
from app.services.weather.exceptions import (
    ProviderConfigError,
    ProviderTimeoutError,
    ProviderApiError,
)
from app.services.weather.cache import weather_cache

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear weather cache before each test."""
    weather_cache.clear()


@pytest.fixture
def mock_weather_response():
    loc = Location(latitude=12.8342, longitude=79.7036, timezone="Asia/Kolkata")
    cur = CurrentWeather(
        latitude=12.8342,
        longitude=79.7036,
        temperature=28.5,
        feels_like=32.0,
        humidity=78.0,
        pressure=1008.0,
        wind_speed=12.5,
        wind_direction=180.0,
        precipitation=0.0,
        condition="Partly Cloudy",
        visibility=10.0,
        observation_time="2026-09-28T14:30:00Z",
        data_source="Mock Provider",
    )
    return WeatherResponse(location=loc, current=cur)


@pytest.fixture
def mock_forecast_response():
    loc = Location(latitude=12.8342, longitude=79.7036, timezone="Asia/Kolkata")
    items = [
        ForecastItem(
            timestamp="2026-09-28T15:00:00Z",
            temperature=29.0,
            feels_like=33.0,
            precipitation_probability=20.0,
            precipitation=0.0,
            humidity=75.0,
            wind_speed=11.0,
            condition="Partly Cloudy",
        )
    ]
    return ForecastResponse(location=loc, forecast=items)


def test_successful_normalization(mock_weather_response):
    assert mock_weather_response.current.temperature == 28.5
    assert mock_weather_response.current.condition == "Partly Cloudy"
    assert mock_weather_response.location.latitude == 12.8342
    assert mock_weather_response.current.data_source == "Mock Provider"


def test_invalid_coordinates():
    # Latitude out of bounds (> 90)
    res_lat = client.get("/api/v1/weather/current?lat=95.0&lon=79.7036")
    assert res_lat.status_code == 400
    assert "Latitude" in res_lat.json()["detail"]

    # Longitude out of bounds (< -180)
    res_lon = client.get("/api/v1/weather/current?lat=12.8342&lon=-190.0")
    assert res_lon.status_code == 400
    assert "Longitude" in res_lon.json()["detail"]


@patch("app.api.v1.endpoints.weather.weather_service.get_current_weather")
def test_current_weather_endpoint_success(mock_get_current, mock_weather_response):
    mock_get_current.return_value = mock_weather_response

    res = client.get("/api/v1/weather/current?lat=12.8342&lon=79.7036")
    assert res.status_code == 200
    data = res.json()
    assert data["current"]["temperature"] == 28.5
    assert data["current"]["condition"] == "Partly Cloudy"
    assert data["current"]["data_source"] == "Mock Provider"


@patch("app.api.v1.endpoints.weather.weather_service.get_forecast")
def test_forecast_endpoint_success(mock_get_forecast, mock_forecast_response):
    mock_get_forecast.return_value = mock_forecast_response

    res = client.get("/api/v1/weather/forecast?lat=12.8342&lon=79.7036")
    assert res.status_code == 200
    data = res.json()
    assert len(data["forecast"]) == 1
    assert data["forecast"][0]["temperature"] == 29.0


@patch("app.api.v1.endpoints.weather.weather_service.get_current_weather")
def test_provider_failure_handling(mock_get_current):
    mock_get_current.side_effect = ProviderApiError("External API returned HTTP 500", status_code=502)

    res = client.get("/api/v1/weather/current?lat=12.8342&lon=79.7036")
    assert res.status_code == 502
    assert "External API returned HTTP 500" in res.json()["detail"]


@patch("app.api.v1.endpoints.weather.weather_service.get_current_weather")
def test_provider_timeout_handling(mock_get_current):
    mock_get_current.side_effect = ProviderTimeoutError("Weather API request timed out")

    res = client.get("/api/v1/weather/current?lat=12.8342&lon=79.7036")
    assert res.status_code == 504
    assert "timed out" in res.json()["detail"]


def test_missing_configuration():
    provider = OpenWeatherProvider(api_key="")

    async def _test():
        with pytest.raises(ProviderConfigError) as exc_info:
            await provider.get_current_weather(12.8342, 79.7036)
        assert "OpenWeather API key is not configured" in str(exc_info.value)

    asyncio.run(_test())
