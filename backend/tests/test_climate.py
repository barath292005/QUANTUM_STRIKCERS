import pytest
from unittest.mock import AsyncMock, patch
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.services.climate.schemas import HistoricalObservationItem
from app.services.climate.analytics import (
    calculate_summary,
    calculate_comparison_metric,
    calculate_trend,
)
from app.services.weather.schemas import Location
from app.services.climate.exceptions import InvalidDateRangeError
from app.services.weather.exceptions import InvalidCoordinatesError

client = TestClient(app)


@pytest.fixture
def sample_records():
    return [
        HistoricalObservationItem(
            timestamp="2026-08-01T00:00:00Z",
            temperature=25.0,
            feels_like=26.0,
            humidity=80.0,
            pressure=1010.0,
            precipitation=5.0,
            wind_speed=10.0,
            wind_direction=180.0,
            condition="Rain",
            data_source="Test Provider",
        ),
        HistoricalObservationItem(
            timestamp="2026-08-02T00:00:00Z",
            temperature=27.0,
            feels_like=28.0,
            humidity=75.0,
            pressure=1012.0,
            precipitation=15.0,
            wind_speed=12.0,
            wind_direction=190.0,
            condition="Rain",
            data_source="Test Provider",
        ),
        HistoricalObservationItem(
            timestamp="2026-08-03T00:00:00Z",
            temperature=29.0,
            feels_like=30.0,
            humidity=70.0,
            pressure=1014.0,
            precipitation=0.0,
            wind_speed=14.0,
            wind_direction=200.0,
            condition="Clear",
            data_source="Test Provider",
        ),
    ]


def test_calculate_summary(sample_records):
    loc = Location(latitude=12.8342, longitude=79.7036)
    summary = calculate_summary(sample_records, loc, "2026-08-01", "2026-08-03")

    assert summary.total_observations == 3
    assert summary.temp_avg == 27.0
    assert summary.temp_min == 25.0
    assert summary.temp_max == 29.0
    assert summary.rainfall_total == 20.0
    assert summary.rainfall_avg == round(20.0 / 3, 2)
    assert summary.humidity_avg == round((80 + 75 + 70) / 3, 2)


def test_comparison_metric_above_average():
    metric = calculate_comparison_metric(32.0, 28.0, is_rainfall=False)
    assert metric.current_value == 32.0
    assert metric.historical_average == 28.0
    assert metric.difference == 4.0
    assert metric.percentage_difference == 14.29
    assert metric.anomaly == "above_average"


def test_comparison_metric_below_average():
    metric = calculate_comparison_metric(22.0, 28.0, is_rainfall=False)
    assert metric.difference == -6.0
    assert metric.anomaly == "below_average"


def test_calculate_trend_increasing(sample_records):
    loc = Location(latitude=12.8342, longitude=79.7036)
    trend = calculate_trend(sample_records, loc, "temperature", "2026-08-01", "2026-08-03")

    assert trend.observations_count == 3
    assert trend.slope > 0  # Temps go 25 -> 27 -> 29 (slope = 2.0 per day)
    assert trend.direction == "increasing"


def test_climate_endpoint_invalid_coordinates():
    res = client.get("/api/v1/climate/history?lat=100.0&lon=79.7036&start_date=2026-08-01&end_date=2026-08-03")
    assert res.status_code == 400
    assert "Latitude" in res.json()["detail"]


def test_climate_endpoint_invalid_date_range():
    # start_date > end_date
    res = client.get("/api/v1/climate/history?lat=12.8342&lon=79.7036&start_date=2026-08-10&end_date=2026-08-01")
    assert res.status_code == 400
    assert "cannot be later than" in res.json()["detail"]

    # Invalid format YYYY/MM/DD
    res_fmt = client.get("/api/v1/climate/history?lat=12.8342&lon=79.7036&start_date=01-08-2026&end_date=2026-08-03")
    assert res_fmt.status_code == 400
    assert "Invalid start_date" in res_fmt.json()["detail"]


@patch("app.api.v1.endpoints.climate.climate_service.get_history")
def test_history_endpoint_success(mock_get_history, sample_records):
    from app.services.climate.schemas import HistoricalDataResponse

    loc = Location(latitude=12.8342, longitude=79.7036)
    mock_get_history.return_value = HistoricalDataResponse(
        location=loc,
        start_date="2026-08-01",
        end_date="2026-08-03",
        total_records=3,
        records=sample_records,
    )

    res = client.get("/api/v1/climate/history?lat=12.8342&lon=79.7036&start_date=2026-08-01&end_date=2026-08-03")
    assert res.status_code == 200
    data = res.json()
    assert data["total_records"] == 3
    assert len(data["records"]) == 3


@patch("app.api.v1.endpoints.climate.climate_service.get_summary")
def test_summary_endpoint_success(mock_get_summary):
    from app.services.climate.schemas import ClimateSummaryResponse

    loc = Location(latitude=12.8342, longitude=79.7036)
    mock_get_summary.return_value = ClimateSummaryResponse(
        location=loc,
        start_date="2026-08-01",
        end_date="2026-08-03",
        total_observations=3,
        period_days=3,
        temp_avg=27.0,
        temp_min=25.0,
        temp_max=29.0,
        rainfall_avg=6.67,
        rainfall_total=20.0,
        humidity_avg=75.0,
        wind_speed_avg=12.0,
    )

    res = client.get("/api/v1/climate/summary?lat=12.8342&lon=79.7036&start_date=2026-08-01&end_date=2026-08-03")
    assert res.status_code == 200
    data = res.json()
    assert data["temp_avg"] == 27.0
    assert data["rainfall_total"] == 20.0


@patch("app.api.v1.endpoints.climate.climate_service.get_trend")
def test_trend_endpoint_success(mock_get_trend):
    from app.services.climate.schemas import ClimateTrendResponse

    loc = Location(latitude=12.8342, longitude=79.7036)
    mock_get_trend.return_value = ClimateTrendResponse(
        location=loc,
        variable="temperature",
        start_date="2026-08-01",
        end_date="2026-08-03",
        observations_count=3,
        period_days=3,
        slope=2.0,
        direction="increasing",
    )

    res = client.get("/api/v1/climate/trend?lat=12.8342&lon=79.7036&start_date=2026-08-01&end_date=2026-08-03&variable=temperature")
    assert res.status_code == 200
    data = res.json()
    assert data["slope"] == 2.0
    assert data["direction"] == "increasing"
