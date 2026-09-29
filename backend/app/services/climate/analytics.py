import math
from datetime import datetime, date
from typing import List, Tuple
from app.services.climate.schemas import (
    HistoricalObservationItem,
    ClimateSummaryResponse,
    ClimateComparisonResponse,
    ComparisonMetric,
    ClimateTrendResponse,
)
from app.services.weather.schemas import Location


def calculate_summary(
    records: List[HistoricalObservationItem],
    location: Location,
    start_date: str,
    end_date: str,
) -> ClimateSummaryResponse:
    if not records:
        return ClimateSummaryResponse(
            location=location,
            start_date=start_date,
            end_date=end_date,
            total_observations=0,
            period_days=0,
            temp_avg=0.0,
            temp_min=0.0,
            temp_max=0.0,
            rainfall_avg=0.0,
            rainfall_total=0.0,
            humidity_avg=0.0,
            wind_speed_avg=0.0,
        )

    temps = [r.temperature for r in records]
    precips = [r.precipitation for r in records]
    humidities = [r.humidity for r in records]
    winds = [r.wind_speed for r in records]

    # Calculate period days
    d_start = datetime.strptime(start_date, "%Y-%m-%d").date() if isinstance(start_date, str) else start_date
    d_end = datetime.strptime(end_date, "%Y-%m-%d").date() if isinstance(end_date, str) else end_date
    period_days = max((d_end - d_start).days + 1, 1)

    total_obs = len(records)
    temp_avg = sum(temps) / total_obs
    temp_min = min(temps)
    temp_max = max(temps)

    rainfall_total = sum(precips)
    rainfall_avg = rainfall_total / period_days

    humidity_avg = sum(humidities) / total_obs
    wind_speed_avg = sum(winds) / total_obs

    return ClimateSummaryResponse(
        location=location,
        start_date=start_date,
        end_date=end_date,
        total_observations=total_obs,
        period_days=period_days,
        temp_avg=round(temp_avg, 2),
        temp_min=round(temp_min, 2),
        temp_max=round(temp_max, 2),
        rainfall_avg=round(rainfall_avg, 2),
        rainfall_total=round(rainfall_total, 2),
        humidity_avg=round(humidity_avg, 2),
        wind_speed_avg=round(wind_speed_avg, 2),
    )


def calculate_comparison_metric(current_val: float, baseline_avg: float, is_rainfall: bool = False) -> ComparisonMetric:
    diff = current_val - baseline_avg
    pct_diff = None
    if baseline_avg != 0:
        pct_diff = round((diff / abs(baseline_avg)) * 100.0, 2)

    # Anomaly classification based on statistical difference
    threshold = 0.5 if not is_rainfall else 1.0
    if diff > threshold:
        anomaly = "above_average"
    elif diff < -threshold:
        anomaly = "below_average"
    else:
        anomaly = "normal"

    return ComparisonMetric(
        current_value=round(current_val, 2),
        historical_average=round(baseline_avg, 2),
        difference=round(diff, 2),
        percentage_difference=pct_diff,
        anomaly=anomaly,
    )


def calculate_trend(
    records: List[HistoricalObservationItem],
    location: Location,
    variable: str,
    start_date: str,
    end_date: str,
) -> ClimateTrendResponse:
    if not records:
        return ClimateTrendResponse(
            location=location,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            observations_count=0,
            period_days=0,
            slope=0.0,
            direction="stable",
        )

    # Sort records by timestamp
    sorted_records = sorted(records, key=lambda r: r.timestamp)
    first_time = datetime.fromisoformat(sorted_records[0].timestamp.replace("Z", "+00:00"))

    # Extract (x_days, y_val)
    points: List[Tuple[float, float]] = []
    for r in sorted_records:
        dt = datetime.fromisoformat(r.timestamp.replace("Z", "+00:00"))
        day_offset = (dt - first_time).total_seconds() / 86400.0

        if variable == "precipitation":
            y_val = r.precipitation
        else:
            y_val = r.temperature

        points.append((day_offset, y_val))

    N = len(points)
    if N < 2:
        return ClimateTrendResponse(
            location=location,
            variable=variable,
            start_date=start_date,
            end_date=end_date,
            observations_count=N,
            period_days=1,
            slope=0.0,
            direction="stable",
        )

    # Ordinary Least Squares (OLS) Linear Regression: slope = sum((x - mean_x)*(y - mean_y)) / sum((x - mean_x)^2)
    mean_x = sum(p[0] for p in points) / N
    mean_y = sum(p[1] for p in points) / N

    num = sum((p[0] - mean_x) * (p[1] - mean_y) for p in points)
    den = sum((p[0] - mean_x) ** 2 for p in points)

    slope = num / den if den != 0 else 0.0

    # Direction threshold (rate per day)
    slope_threshold = 0.005
    if slope > slope_threshold:
        direction = "increasing"
    elif slope < -slope_threshold:
        direction = "decreasing"
    else:
        direction = "stable"

    last_time = datetime.fromisoformat(sorted_records[-1].timestamp.replace("Z", "+00:00"))
    period_days = max((last_time - first_time).days + 1, 1)

    return ClimateTrendResponse(
        location=location,
        variable=variable,
        start_date=start_date,
        end_date=end_date,
        observations_count=N,
        period_days=period_days,
        slope=round(slope, 4),
        direction=direction,
    )
