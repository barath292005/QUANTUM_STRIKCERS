import httpx
from typing import Dict, Any
from app.services.weather.provider import BaseWeatherProvider
from app.services.weather.schemas import (
    Location,
    CurrentWeather,
    WeatherResponse,
    ForecastItem,
    ForecastResponse,
)
from app.services.weather.exceptions import (
    ProviderTimeoutError,
    ProviderApiError,
)

WMO_WEATHER_CODES: Dict[int, str] = {
    0: "Clear Sky",
    1: "Mainly Clear",
    2: "Partly Cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing Rime Fog",
    51: "Light Drizzle",
    53: "Moderate Drizzle",
    55: "Dense Drizzle",
    56: "Light Freezing Drizzle",
    57: "Dense Freezing Drizzle",
    61: "Slight Rain",
    63: "Moderate Rain",
    65: "Heavy Rain",
    66: "Light Freezing Rain",
    67: "Heavy Freezing Rain",
    71: "Slight Snow Fall",
    73: "Moderate Snow Fall",
    75: "Heavy Snow Fall",
    77: "Snow Grains",
    80: "Slight Rain Showers",
    81: "Moderate Rain Showers",
    82: "Violent Rain Showers",
    85: "Slight Snow Showers",
    86: "Heavy Snow Showers",
    95: "Thunderstorm",
    96: "Thunderstorm with Slight Hail",
    99: "Thunderstorm with Heavy Hail",
}


class OpenMeteoProvider(BaseWeatherProvider):
    """
    Open-Meteo Weather API Provider Implementation.
    Fetches real-time weather and forecast data without requiring API keys.
    """

    def __init__(self, base_url: str = "https://api.open-meteo.com/v1", timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "Open-Meteo API"

    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        url = f"{self.base_url}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,wind_speed_10m,wind_direction_10m,precipitation,weather_code",
            "timezone": "auto",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise ProviderApiError(
                        f"Open-Meteo API returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )
                data = response.json()
        except httpx.TimeoutException:
            raise ProviderTimeoutError("Open-Meteo API request timed out after 15.0 seconds")
        except httpx.RequestError as exc:
            raise ProviderApiError(f"Network error connecting to Open-Meteo API: {str(exc)}")

        if "current" not in data:
            raise ProviderApiError("Malformed response from Open-Meteo API: missing 'current' field")

        current = data["current"]
        weather_code = current.get("weather_code", 0)
        condition = WMO_WEATHER_CODES.get(weather_code, f"Weather Code {weather_code}")

        location_obj = Location(
            latitude=data.get("latitude", lat),
            longitude=data.get("longitude", lon),
            timezone=data.get("timezone", "UTC"),
        )

        current_obj = CurrentWeather(
            latitude=location_obj.latitude,
            longitude=location_obj.longitude,
            temperature=float(current.get("temperature_2m", 0.0)),
            feels_like=float(current.get("apparent_temperature", current.get("temperature_2m", 0.0))),
            humidity=float(current.get("relative_humidity_2m", 0.0)),
            pressure=float(current.get("surface_pressure", 1013.25)),
            wind_speed=float(current.get("wind_speed_10m", 0.0)),
            wind_direction=float(current.get("wind_direction_10m", 0.0)),
            precipitation=float(current.get("precipitation", 0.0)),
            condition=condition,
            visibility=None,  # Open-Meteo does not provide visibility in default endpoint
            observation_time=current.get("time", ""),
            data_source=self.provider_name,
        )

        return WeatherResponse(location=location_obj, current=current_obj)

    async def get_forecast(self, lat: float, lon: float) -> ForecastResponse:
        url = f"{self.base_url}/forecast"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,precipitation_probability,precipitation,wind_speed_10m,weather_code",
            "forecast_days": 3,
            "timezone": "auto",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise ProviderApiError(
                        f"Open-Meteo API returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )
                data = response.json()
        except httpx.TimeoutException:
            raise ProviderTimeoutError("Open-Meteo API forecast request timed out after 15.0 seconds")
        except httpx.RequestError as exc:
            raise ProviderApiError(f"Network error connecting to Open-Meteo API: {str(exc)}")

        if "hourly" not in data:
            raise ProviderApiError("Malformed response from Open-Meteo API: missing 'hourly' field")

        hourly = data["hourly"]
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        feels = hourly.get("apparent_temperature", [])
        humidities = hourly.get("relative_humidity_2m", [])
        precip_probs = hourly.get("precipitation_probability", [])
        precips = hourly.get("precipitation", [])
        winds = hourly.get("wind_speed_10m", [])
        codes = hourly.get("weather_code", [])

        location_obj = Location(
            latitude=data.get("latitude", lat),
            longitude=data.get("longitude", lon),
            timezone=data.get("timezone", "UTC"),
        )

        forecast_items = []
        for i in range(min(len(times), 24)):
            code = codes[i] if i < len(codes) else 0
            cond = WMO_WEATHER_CODES.get(code, f"Weather Code {code}")

            item = ForecastItem(
                timestamp=times[i],
                temperature=float(temps[i]) if i < len(temps) else 0.0,
                feels_like=float(feels[i]) if i < len(feels) else None,
                precipitation_probability=float(precip_probs[i]) if i < len(precip_probs) and precip_probs[i] is not None else None,
                precipitation=float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0,
                humidity=float(humidities[i]) if i < len(humidities) else 0.0,
                wind_speed=float(winds[i]) if i < len(winds) else 0.0,
                condition=cond,
            )
            forecast_items.append(item)

        return ForecastResponse(location=location_obj, forecast=forecast_items)
