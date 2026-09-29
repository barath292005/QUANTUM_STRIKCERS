"""Impact-based risk orchestration. Composes WeatherService and ClimateService."""

from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.services.climate.exceptions import ClimateServiceError
from app.services.climate.service import ClimateService
from app.services.risk.exceptions import InsufficientRiskInputsError, InvalidForecastWindowError
from app.services.risk.explainability import build_drivers
from app.services.risk.feature_engine import build_features
from app.services.risk.risk_classifier import HazardRiskModel, TransparentRiskModel, recommendations_for_level
from app.services.risk.schemas import RiskModelInfo, RiskResponse
from app.services.risk.thresholds import (
    CLIMATE_BASELINE_DAYS,
    FORECAST_HOURS_MAX,
    FORECAST_HOURS_MIN,
    HAZARD_ID,
    LIMITATIONS,
    MODEL_NAME,
    MODEL_TYPE,
    MODEL_VERSION,
    RECENT_RAINFALL_DAYS,
)
from app.services.weather.exceptions import InvalidCoordinatesError, WeatherServiceError
from app.services.weather.schemas import Location
from app.services.weather.service import WeatherService

logger = logging.getLogger(__name__)


class RiskService:
    """Coordinates weather + climate inputs into a transparent heavy-rain risk assessment."""

    def __init__(
        self,
        weather_service: Optional[WeatherService] = None,
        climate_service: Optional[ClimateService] = None,
        model: Optional[HazardRiskModel] = None,
    ):
        self.weather_service = weather_service or WeatherService()
        self.climate_service = climate_service or ClimateService()
        self.model: HazardRiskModel = model or TransparentRiskModel()

    def _validate(self, lat: float, lon: float, forecast_hours: int) -> None:
        if not (-90.0 <= lat <= 90.0):
            raise InvalidCoordinatesError(
                f"Invalid latitude {lat}. Latitude must be between -90 and 90 degrees."
            )
        if not (-180.0 <= lon <= 180.0):
            raise InvalidCoordinatesError(
                f"Invalid longitude {lon}. Longitude must be between -180 and 180 degrees."
            )
        if forecast_hours < FORECAST_HOURS_MIN or forecast_hours > FORECAST_HOURS_MAX:
            raise InvalidForecastWindowError(
                f"forecast_hours must be between {FORECAST_HOURS_MIN} and {FORECAST_HOURS_MAX}."
            )

    async def assess(self, lat: float, lon: float, forecast_hours: int, db: Session) -> RiskResponse:
        self._validate(lat, lon, forecast_hours)
        logger.info(
            "risk_assessment_request",
            extra={"lat": lat, "lon": lon, "forecast_hours": forecast_hours},
        )

        current = None
        forecast = None
        weather_error = None
        try:
            current = await self.weather_service.get_current_weather(lat, lon)
        except WeatherServiceError as exc:
            weather_error = exc
            logger.error("risk_current_weather_unavailable", extra={"error": str(exc)})

        try:
            forecast = await self.weather_service.get_forecast(lat, lon)
        except WeatherServiceError as exc:
            logger.error("risk_forecast_unavailable", extra={"error": str(exc)})
            if current is None:
                # Neither live source available — cannot produce a meteorological assessment.
                raise InsufficientRiskInputsError(
                    "Unable to produce a risk assessment because current weather and forecast data are both unavailable."
                ) from (weather_error or exc)

        today = date.today()
        start_baseline = (today - timedelta(days=CLIMATE_BASELINE_DAYS)).isoformat()
        end_baseline = today.isoformat()
        start_recent = (today - timedelta(days=RECENT_RAINFALL_DAYS)).isoformat()

        summary = None
        comparison = None
        history = None
        try:
            summary = await self.climate_service.get_summary(lat, lon, start_baseline, end_baseline, db)
        except (ClimateServiceError, WeatherServiceError) as exc:
            logger.error("risk_climate_summary_unavailable", extra={"error": str(exc)})

        try:
            comparison = await self.climate_service.get_comparison(lat, lon, end_baseline, db)
        except (ClimateServiceError, WeatherServiceError) as exc:
            logger.error("risk_climate_comparison_unavailable", extra={"error": str(exc)})

        try:
            history = await self.climate_service.get_history(lat, lon, start_recent, end_baseline, db)
        except (ClimateServiceError, WeatherServiceError) as exc:
            logger.error("risk_climate_history_unavailable", extra={"error": str(exc)})

        features = build_features(
            current=current,
            forecast=forecast,
            summary=summary,
            comparison=comparison,
            history=history,
            forecast_hours=forecast_hours,
        )

        score, level = self.model.predict(features)
        drivers = build_drivers(features)
        actions = recommendations_for_level(level)

        if current is not None:
            location = current.location
        elif forecast is not None:
            location = forecast.location
        else:
            location = Location(latitude=lat, longitude=lon)

        return RiskResponse(
            location=location,
            hazard=HAZARD_ID,
            risk_level=level,
            risk_score=score,
            forecast_window_hours=forecast_hours,
            features=features,
            drivers=drivers,
            recommended_actions=actions,
            model=RiskModelInfo(name=MODEL_NAME, version=MODEL_VERSION, type=MODEL_TYPE),
            limitations=list(LIMITATIONS),
        )
