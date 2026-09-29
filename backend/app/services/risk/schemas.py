from typing import List, Optional
from pydantic import BaseModel, Field
from app.services.weather.schemas import Location


class RiskFeatures(BaseModel):
    """Observables and derived indicators used by the transparent risk model.

    Any field may be null when the corresponding source did not provide data.
    Units are documented on each field; derived ratios are dimensionless.
    """

    current_precipitation: Optional[float] = Field(
        None, description="Current precipitation amount from WeatherService (mm as reported by the provider)"
    )
    forecast_precipitation: Optional[float] = Field(
        None, description="Sum of forecast precipitation over the assessment window (mm)"
    )
    historical_rainfall_baseline: Optional[float] = Field(
        None, description="ClimateService 30-day average daily rainfall (mm/day)"
    )
    rainfall_anomaly: Optional[float] = Field(
        None,
        description=(
            "Relative rainfall anomaly as a ratio: "
            "(forecast daily equivalent - baseline) / baseline. "
            "0.5 means 50% above the historical daily baseline. Null if baseline is missing or zero."
        ),
    )
    recent_rainfall: Optional[float] = Field(
        None, description="Sum of historical precipitation over the recent lookback window (mm)"
    )
    humidity: Optional[float] = Field(None, description="Current relative humidity (%)")
    wind_speed: Optional[float] = Field(None, description="Current wind speed (km/h)")
    forecast_daily_equivalent: Optional[float] = Field(
        None,
        description="Forecast precipitation scaled to a 24-hour rate: sum * (24 / forecast_hours) (mm/day)",
    )
    forecast_rainfall_excess: Optional[float] = Field(
        None,
        description="Forecast daily-equivalent rainfall minus historical daily baseline (mm/day)",
    )
    precipitation_persistence: Optional[float] = Field(
        None,
        description="Fraction of forecast steps in the window with precipitation above the wet-step trace (0.0–1.0)",
    )
    precipitation_intensity_indicator: Optional[float] = Field(
        None, description="Maximum precipitation in a single forecast step within the window (mm)"
    )


class RiskDriver(BaseModel):
    feature: str = Field(..., description="Feature key that contributed to this explanation")
    value: Optional[float] = Field(None, description="Numeric value of the feature, if available")
    direction: str = Field(..., description="'increases_risk' or 'decreases_risk'")
    message: str = Field(..., description="Plain-language explanation grounded in the feature value")


class RiskModelInfo(BaseModel):
    name: str
    version: str
    type: str


class RiskResponse(BaseModel):
    location: Location
    hazard: str = Field(..., description="Hazard identifier (currently only 'heavy_rain_flood')")
    risk_level: str = Field(..., description="LOW, MODERATE, HIGH, or EXTREME")
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Composite prototype score in [0.0, 1.0]")
    forecast_window_hours: int
    features: RiskFeatures
    drivers: List[RiskDriver] = Field(default_factory=list)
    recommended_actions: List[str] = Field(default_factory=list)
    model: RiskModelInfo
    limitations: List[str] = Field(default_factory=list)
