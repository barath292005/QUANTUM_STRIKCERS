from typing import List, Optional
from pydantic import BaseModel, Field, field_validator


class Location(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate (-90 to 90)")
    longitude: float = Field(..., description="Longitude coordinate (-180 to 180)")
    city: Optional[str] = Field(None, description="City or location region name")
    country: Optional[str] = Field(None, description="Country code or country name")
    timezone: Optional[str] = Field(None, description="Timezone offset or identifier")

    @field_validator("latitude")
    def validate_latitude(cls, v: float) -> float:
        if not (-90.0 <= v <= 90.0):
            raise ValueError("Latitude must be between -90 and 90 degrees")
        return round(v, 4)

    @field_validator("longitude")
    def validate_longitude(cls, v: float) -> float:
        if not (-180.0 <= v <= 180.0):
            raise ValueError("Longitude must be between -180 and 180 degrees")
        return round(v, 4)


class CurrentWeather(BaseModel):
    latitude: float = Field(..., description="Latitude coordinate")
    longitude: float = Field(..., description="Longitude coordinate")
    temperature: float = Field(..., description="Current temperature in Celsius (°C)")
    feels_like: float = Field(..., description="Apparent temperature in Celsius (°C)")
    humidity: float = Field(..., description="Relative humidity percentage (%)")
    pressure: float = Field(..., description="Atmospheric pressure at surface in hPa")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    wind_direction: float = Field(..., description="Wind direction in degrees (0-360°)")
    precipitation: float = Field(..., description="Precipitation rate in mm")
    condition: str = Field(..., description="Current weather condition text")
    visibility: Optional[float] = Field(None, description="Visibility in km")
    observation_time: str = Field(..., description="Observation timestamp in ISO 8601 string format")
    data_source: str = Field(..., description="Provider source identifier")


class ForecastItem(BaseModel):
    timestamp: str = Field(..., description="Forecast timestamp in ISO 8601 format")
    temperature: float = Field(..., description="Forecast temperature in Celsius (°C)")
    feels_like: Optional[float] = Field(None, description="Apparent temperature in Celsius (°C)")
    precipitation_probability: Optional[float] = Field(None, description="Precipitation probability percentage (%)")
    precipitation: Optional[float] = Field(None, description="Precipitation amount in mm")
    humidity: float = Field(..., description="Relative humidity percentage (%)")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    condition: str = Field(..., description="Weather condition description")


class WeatherResponse(BaseModel):
    location: Location
    current: CurrentWeather


class ForecastResponse(BaseModel):
    location: Location
    forecast: List[ForecastItem]
