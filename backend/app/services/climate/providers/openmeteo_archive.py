import httpx
from datetime import date
from typing import List
from app.services.climate.provider import BaseHistoricalProvider
from app.services.climate.schemas import HistoricalObservationItem
from app.services.weather.providers.openmeteo import WMO_WEATHER_CODES
from app.services.weather.exceptions import ProviderTimeoutError, ProviderApiError


class OpenMeteoArchiveProvider(BaseHistoricalProvider):
    """
    Open-Meteo Historical Archive API Provider Implementation.
    Queries historical climate datasets from reanalysis models (ERA5/ERA5-Land).
    """

    def __init__(self, base_url: str = "https://archive-api.open-meteo.com/v1", timeout: float = 12.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    @property
    def provider_name(self) -> str:
        return "Open-Meteo Historical Archive API"

    async def fetch_historical_observations(
        self, lat: float, lon: float, start_date: date, end_date: date
    ) -> List[HistoricalObservationItem]:
        url = f"{self.base_url}/archive"
        params = {
            "latitude": lat,
            "longitude": lon,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "hourly": "temperature_2m,relative_humidity_2m,apparent_temperature,surface_pressure,precipitation,wind_speed_10m,wind_direction_10m,weather_code",
            "timezone": "auto",
        }

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, params=params)
                if response.status_code != 200:
                    raise ProviderApiError(
                        f"Open-Meteo Archive API returned HTTP {response.status_code}: {response.text}",
                        status_code=response.status_code,
                    )
                data = response.json()
        except httpx.TimeoutException:
            raise ProviderTimeoutError("Open-Meteo Archive API request timed out after 12.0 seconds")
        except httpx.RequestError as exc:
            raise ProviderApiError(f"Network error connecting to Open-Meteo Archive API: {str(exc)}")

        if "hourly" not in data:
            raise ProviderApiError("Malformed response from Open-Meteo Archive API: missing 'hourly' field")

        hourly = data["hourly"]
        times = hourly.get("time", [])
        temps = hourly.get("temperature_2m", [])
        feels = hourly.get("apparent_temperature", [])
        humidities = hourly.get("relative_humidity_2m", [])
        pressures = hourly.get("surface_pressure", [])
        precips = hourly.get("precipitation", [])
        winds = hourly.get("wind_speed_10m", [])
        dirs = hourly.get("wind_direction_10m", [])
        codes = hourly.get("weather_code", [])

        records: List[HistoricalObservationItem] = []
        for i in range(len(times)):
            code = codes[i] if i < len(codes) else 0
            cond = WMO_WEATHER_CODES.get(code, f"Weather Code {code}")

            item = HistoricalObservationItem(
                timestamp=times[i],
                temperature=float(temps[i]) if i < len(temps) and temps[i] is not None else 0.0,
                feels_like=float(feels[i]) if i < len(feels) and feels[i] is not None else None,
                humidity=float(humidities[i]) if i < len(humidities) and humidities[i] is not None else 0.0,
                pressure=float(pressures[i]) if i < len(pressures) and pressures[i] is not None else 1013.25,
                precipitation=float(precips[i]) if i < len(precips) and precips[i] is not None else 0.0,
                wind_speed=float(winds[i]) if i < len(winds) and winds[i] is not None else 0.0,
                wind_direction=float(dirs[i]) if i < len(dirs) and dirs[i] is not None else 0.0,
                condition=cond,
                data_source=self.provider_name,
            )
            records.append(item)

        return records
