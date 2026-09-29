import httpx
from typing import Optional
from app.services.weather.provider import BaseWeatherProvider
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


class OpenWeatherProvider(BaseWeatherProvider):
    """
    OpenWeatherMap Weather API Provider Implementation.
    Requires an OPENWEATHER_API_KEY environment variable.
    """

    def __init__(self, api_key: Optional[str] = None, timeout: float = 8.0):
        self.api_key = api_key
        self.timeout = timeout
        self.base_url = "https://api.openweathermap.org/data/2.5"

    @property
    def provider_name(self) -> str:
        return "OpenWeatherMap API"

    async def get_current_weather(self, lat: float, lon: float) -> WeatherResponse:
        if not self.api_key:
            raise ProviderConfigError(
                "OpenWeather API key is not configured. Please set OPENWEATHER_API_KEY in backend/.env"
            )

        url = f"{self.base_url}/weather"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise ProviderApiError(
                        f"OpenWeather API returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )
                data = response.json()
        except httpx.TimeoutException:
            raise ProviderTimeoutError("OpenWeather API current weather request timed out")
        except httpx.RequestError as exc:
            raise ProviderApiError(f"Network error connecting to OpenWeather API: {str(exc)}")

        main = data.get("main", {})
        wind = data.get("wind", {})
        rain = data.get("rain", {})
        weather_list = data.get("weather", [{}])
        cond_text = weather_list[0].get("main", "Clear") if weather_list else "Clear"

        location_obj = Location(
            latitude=lat,
            longitude=lon,
            city=data.get("name"),
            country=data.get("sys", {}).get("country"),
        )

        current_obj = CurrentWeather(
            latitude=lat,
            longitude=lon,
            temperature=float(main.get("temp", 0.0)),
            feels_like=float(main.get("feels_like", main.get("temp", 0.0))),
            humidity=float(main.get("humidity", 0.0)),
            pressure=float(main.get("pressure", 1013.25)),
            wind_speed=float(wind.get("speed", 0.0)) * 3.6,  # m/s to km/h
            wind_direction=float(wind.get("deg", 0.0)),
            precipitation=float(rain.get("1h", 0.0)),
            condition=cond_text,
            visibility=float(data.get("visibility", 10000)) / 1000.0 if "visibility" in data else None,
            observation_time=str(data.get("dt", "")),
            data_source=self.provider_name,
        )

        return WeatherResponse(location=location_obj, current=current_obj)

    async def get_forecast(self, lat: float, lon: float) -> ForecastResponse:
        if not self.api_key:
            raise ProviderConfigError(
                "OpenWeather API key is not configured. Please set OPENWEATHER_API_KEY in backend/.env"
            )

        url = f"{self.base_url}/forecast"
        params = {
            "lat": lat,
            "lon": lon,
            "appid": self.api_key,
            "units": "metric",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise ProviderApiError(
                        f"OpenWeather API returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )
                data = response.json()
        except httpx.TimeoutException:
            raise ProviderTimeoutError("OpenWeather API forecast request timed out")
        except httpx.RequestError as exc:
            raise ProviderApiError(f"Network error connecting to OpenWeather API: {str(exc)}")

        location_obj = Location(
            latitude=lat,
            longitude=lon,
            city=data.get("city", {}).get("name"),
            country=data.get("city", {}).get("country"),
        )

        raw_list = data.get("list", [])
        items = []
        for entry in raw_list[:24]:
            main = entry.get("main", {})
            w_list = entry.get("weather", [{}])
            wind = entry.get("wind", {})
            rain = entry.get("rain", {})
            cond = w_list[0].get("main", "Clear") if w_list else "Clear"

            item = ForecastItem(
                timestamp=entry.get("dt_txt", str(entry.get("dt", ""))),
                temperature=float(main.get("temp", 0.0)),
                feels_like=float(main.get("feels_like", main.get("temp", 0.0))),
                precipitation_probability=float(entry.get("pop", 0.0)) * 100.0,
                precipitation=float(rain.get("3h", 0.0)),
                humidity=float(main.get("humidity", 0.0)),
                wind_speed=float(wind.get("speed", 0.0)) * 3.6,
                condition=cond,
            )
            items.append(item)

        return ForecastResponse(location=location_obj, forecast=items)
