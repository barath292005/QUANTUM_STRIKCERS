"""Feature engineering for heavy-rain / flood-related risk indicators.

Every derived value is computed from WeatherService / ClimateService payloads.
Unavailable source fields remain None; this module never invents values.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional, Sequence

from app.services.climate.schemas import ClimateComparisonResponse, ClimateSummaryResponse, HistoricalDataResponse
from app.services.risk.schemas import RiskFeatures
from app.services.risk.thresholds import RECENT_RAINFALL_DAYS, WET_STEP_PRECIP_MM
from app.services.weather.schemas import ForecastItem, ForecastResponse, WeatherResponse

logger = logging.getLogger(__name__)


def _parse_timestamp(value: str) -> Optional[datetime]:
    if not value:
        return None
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt
    except ValueError:
        return None


def select_forecast_window(
    forecast: Optional[ForecastResponse],
    forecast_hours: int,
    now: Optional[datetime] = None,
) -> List[ForecastItem]:
    """Return forecast items that fall inside the requested window.

    Calculation:
    - Parse each item timestamp.
    - Keep items with time in [now - 1 hour, now + forecast_hours].
    - If no timestamp parses or none fall in range, assume hourly steps and
      take the first `forecast_hours` items (Open-Meteo hourly forecast).
    """
    if forecast is None or not forecast.forecast:
        return []

    items = forecast.forecast
    origin = now or datetime.now(timezone.utc)
    window_end = origin + timedelta(hours=forecast_hours)
    window_start = origin - timedelta(hours=1)

    selected: List[ForecastItem] = []
    parsed_any = False
    for item in items:
        dt = _parse_timestamp(item.timestamp)
        if dt is None:
            continue
        parsed_any = True
        if window_start <= dt <= window_end:
            selected.append(item)

    if selected:
        return selected
    if parsed_any:
        # Timestamps exist but sit outside "now" (e.g. mocked clocks). Use the
        # first item as t0 and keep items within forecast_hours of t0.
        first_dt = _parse_timestamp(items[0].timestamp)
        if first_dt is not None:
            end = first_dt + timedelta(hours=forecast_hours)
            return [i for i in items if (dt := _parse_timestamp(i.timestamp)) is not None and first_dt <= dt <= end]
    return list(items[: max(forecast_hours, 0)])


def _sum_precip(items: Sequence[ForecastItem]) -> Optional[float]:
    values = [item.precipitation for item in items if item.precipitation is not None]
    if not values:
        return None
    return round(sum(values), 4)


def _max_precip(items: Sequence[ForecastItem]) -> Optional[float]:
    values = [item.precipitation for item in items if item.precipitation is not None]
    if not values:
        return None
    return round(max(values), 4)


def _persistence(items: Sequence[ForecastItem]) -> Optional[float]:
    """Fraction of steps with precipitation > WET_STEP_PRECIP_MM."""
    counted = [item.precipitation for item in items if item.precipitation is not None]
    if not counted:
        return None
    wet = sum(1 for v in counted if v > WET_STEP_PRECIP_MM)
    return round(wet / len(counted), 4)


def _recent_rainfall_sum(history: Optional[HistoricalDataResponse]) -> Optional[float]:
    """Sum precipitation on records whose timestamp falls in the recent window.

    Calculation: sum(record.precipitation) for records with
    timestamp >= (max_timestamp - RECENT_RAINFALL_DAYS), using the latest
    observation as the window end so mocked/historical clocks still work.
    """
    if history is None or not history.records:
        return None
    parsed = []
    for rec in history.records:
        dt = _parse_timestamp(rec.timestamp)
        if dt is not None:
            parsed.append((dt, rec.precipitation))
    if not parsed:
        return None
    latest = max(p[0] for p in parsed)
    cutoff = latest - timedelta(days=RECENT_RAINFALL_DAYS)
    window = [precip for dt, precip in parsed if dt >= cutoff]
    if not window:
        return None
    return round(sum(window), 4)


def build_features(
    current: Optional[WeatherResponse],
    forecast: Optional[ForecastResponse],
    summary: Optional[ClimateSummaryResponse],
    comparison: Optional[ClimateComparisonResponse],
    history: Optional[HistoricalDataResponse],
    forecast_hours: int,
) -> RiskFeatures:
    """Assemble RiskFeatures from optional upstream payloads.

    Feature calculations
    --------------------
    current_precipitation:
        WeatherResponse.current.precipitation (mm, provider-reported).

    forecast_precipitation:
        Sum of ForecastItem.precipitation over the selected window (mm).

    historical_rainfall_baseline:
        ClimateSummaryResponse.rainfall_avg — mean daily rainfall (mm/day)
        over the climate lookback used by RiskService.

    rainfall_anomaly:
        Let F = forecast_precipitation, H = forecast_hours, B = baseline.
        Daily equivalent D = F * (24 / H).
        Anomaly ratio A = (D - B) / B when B > 0, else None.
        If forecast precip is missing, fall back to ClimateService comparison
        percentage_difference / 100 when that value is present.

    recent_rainfall:
        Sum of historical precipitation over RECENT_RAINFALL_DAYS (mm).

    humidity / wind_speed:
        Current weather humidity (%) and wind_speed (km/h).

    forecast_rainfall_excess:
        D - B (mm/day) when both D and B are available.

    precipitation_persistence:
        (# steps with precip > WET_STEP_PRECIP_MM) / (# steps with precip).

    precipitation_intensity_indicator:
        Max ForecastItem.precipitation in the window (mm).
    """
    window = select_forecast_window(forecast, forecast_hours)

    current_precip = None
    humidity = None
    wind_speed = None
    if current is not None:
        current_precip = current.current.precipitation
        humidity = current.current.humidity
        wind_speed = current.current.wind_speed

    forecast_precip = _sum_precip(window) if window else None
    intensity = _max_precip(window) if window else None
    persistence = _persistence(window) if window else None

    baseline = None
    if summary is not None:
        baseline = summary.rainfall_avg

    if summary is not None and summary.total_observations == 0:
        baseline = None

    daily_equivalent = None
    if forecast_precip is not None and forecast_hours > 0:
        daily_equivalent = round(forecast_precip * (24.0 / float(forecast_hours)), 4)

    anomaly = None
    excess = None
    if daily_equivalent is not None and baseline is not None and baseline > 0:
        anomaly = round((daily_equivalent - baseline) / baseline, 4)
        excess = round(daily_equivalent - baseline, 4)
    elif comparison is not None and comparison.rainfall.percentage_difference is not None:
        # Fallback: ClimateService comparison uses current precip vs 30-day avg.
        anomaly = round(comparison.rainfall.percentage_difference / 100.0, 4)

    recent = _recent_rainfall_sum(history)

    features = RiskFeatures(
        current_precipitation=current_precip,
        forecast_precipitation=forecast_precip,
        historical_rainfall_baseline=baseline,
        rainfall_anomaly=anomaly,
        recent_rainfall=recent,
        humidity=humidity,
        wind_speed=wind_speed,
        forecast_daily_equivalent=daily_equivalent,
        forecast_rainfall_excess=excess,
        precipitation_persistence=persistence,
        precipitation_intensity_indicator=intensity,
    )
    logger.info(
        "risk_feature_generation",
        extra={
            "forecast_hours": forecast_hours,
            "window_steps": len(window),
            "has_current": current is not None,
            "has_forecast": forecast is not None,
            "has_summary": summary is not None,
            "has_history": history is not None,
        },
    )
    return features
