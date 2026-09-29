from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
from app.services.weather.schemas import Location


class HistoricalObservationItem(BaseModel):
    timestamp: str = Field(..., description="Observation timestamp in ISO 8601 format (YYYY-MM-DDTHH:MM:SS)")
    temperature: float = Field(..., description="Observed temperature in Celsius (°C)")
    feels_like: Optional[float] = Field(None, description="Apparent temperature in Celsius (°C)")
    humidity: float = Field(..., description="Relative humidity percentage (%)")
    pressure: float = Field(..., description="Surface barometric pressure in hPa")
    precipitation: float = Field(..., description="Precipitation amount in mm")
    wind_speed: float = Field(..., description="Wind speed in km/h")
    wind_direction: float = Field(..., description="Wind direction in degrees (0-360°)")
    condition: str = Field(..., description="Observed weather condition")
    data_source: str = Field(..., description="Source of historical observation record")


class HistoricalDataResponse(BaseModel):
    location: Location
    start_date: str
    end_date: str
    total_records: int
    records: List[HistoricalObservationItem]


class ClimateSummaryResponse(BaseModel):
    location: Location
    start_date: str
    end_date: str
    total_observations: int
    period_days: int
    temp_avg: float = Field(..., description="Daily average temperature in °C")
    temp_min: float = Field(..., description="Minimum recorded temperature in °C")
    temp_max: float = Field(..., description="Maximum recorded temperature in °C")
    rainfall_avg: float = Field(..., description="Average daily rainfall in mm")
    rainfall_total: float = Field(..., description="Cumulative total rainfall in mm")
    humidity_avg: float = Field(..., description="Average relative humidity percentage (%)")
    wind_speed_avg: float = Field(..., description="Average wind speed in km/h")


class ComparisonMetric(BaseModel):
    current_value: float = Field(..., description="Current observed value")
    historical_average: float = Field(..., description="Historical baseline average")
    difference: float = Field(..., description="Absolute difference (current - baseline)")
    percentage_difference: Optional[float] = Field(None, description="Percentage change relative to baseline")
    anomaly: str = Field(..., description="Anomaly classification ('above_average', 'below_average', 'normal')")


class ClimateComparisonResponse(BaseModel):
    location: Location
    target_date: str
    temperature: ComparisonMetric
    rainfall: ComparisonMetric


class ClimateTrendResponse(BaseModel):
    location: Location
    variable: str = Field(..., description="Analyzed variable (e.g. 'temperature', 'precipitation')")
    start_date: str
    end_date: str
    observations_count: int
    period_days: int
    slope: float = Field(..., description="Linear regression slope rate (change per day)")
    direction: str = Field(..., description="Trend direction: 'increasing', 'decreasing', or 'stable'")
