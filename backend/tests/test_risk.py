import pytest
from unittest.mock import AsyncMock, patch
from fastapi.testclient import TestClient

from app.main import app
from app.services.climate.schemas import (
    ClimateComparisonResponse,
    ClimateSummaryResponse,
    ComparisonMetric,
    HistoricalDataResponse,
    HistoricalObservationItem,
)
from app.services.risk.explainability import build_drivers
from app.services.risk.feature_engine import build_features
from app.services.risk.risk_classifier import (
    TransparentRiskModel,
    classify_risk_level,
    recommendations_for_level,
)
from app.services.risk.schemas import RiskFeatures
from app.services.weather.exceptions import ProviderApiError
from app.services.weather.schemas import (
    CurrentWeather,
    ForecastItem,
    ForecastResponse,
    Location,
    WeatherResponse,
)

client = TestClient(app)


def _location():
    return Location(latitude=12.8342, longitude=79.7036, timezone="Asia/Kolkata")


def _current(precip=2.0, humidity=85.0, wind=12.0):
    loc = _location()
    return WeatherResponse(
        location=loc,
        current=CurrentWeather(
            latitude=12.8342,
            longitude=79.7036,
            temperature=28.0,
            feels_like=31.0,
            humidity=humidity,
            pressure=1008.0,
            wind_speed=wind,
            wind_direction=180.0,
            precipitation=precip,
            condition="Rain",
            visibility=None,
            observation_time="2026-09-28T14:00:00Z",
            data_source="Mock Provider",
        ),
    )


def _forecast(hourly_mm):
    items = []
    for i, mm in enumerate(hourly_mm):
        hour = 15 + i
        items.append(
            ForecastItem(
                timestamp=f"2020-01-01T{hour:02d}:00:00Z",
                temperature=28.0,
                feels_like=31.0,
                precipitation_probability=80.0,
                precipitation=mm,
                humidity=85.0,
                wind_speed=12.0,
                condition="Rain",
            )
        )
    return ForecastResponse(location=_location(), forecast=items)


def _summary(rainfall_avg=5.0, observations=10):
    return ClimateSummaryResponse(
        location=_location(),
        start_date="2026-08-29",
        end_date="2026-09-28",
        total_observations=observations,
        period_days=30,
        temp_avg=28.0,
        temp_min=24.0,
        temp_max=32.0,
        rainfall_avg=rainfall_avg,
        rainfall_total=rainfall_avg * 30,
        humidity_avg=80.0,
        wind_speed_avg=10.0,
    )


def _comparison(pct=40.0):
    metric = ComparisonMetric(
        current_value=7.0,
        historical_average=5.0,
        difference=2.0,
        percentage_difference=pct,
        anomaly="above_average",
    )
    return ClimateComparisonResponse(
        location=_location(),
        target_date="2026-09-28",
        temperature=metric,
        rainfall=metric,
    )


def _history(values):
    records = []
    for i, mm in enumerate(values):
        records.append(
            HistoricalObservationItem(
                timestamp=f"2026-09-{22 + i:02d}T00:00:00Z",
                temperature=27.0,
                feels_like=28.0,
                humidity=80.0,
                pressure=1010.0,
                precipitation=mm,
                wind_speed=10.0,
                wind_direction=180.0,
                condition="Rain",
                data_source="Mock Archive",
            )
        )
    return HistoricalDataResponse(
        location=_location(),
        start_date="2026-09-22",
        end_date="2026-09-28",
        total_records=len(records),
        records=records,
    )


def test_feature_calculation_core_fields():
    features = build_features(
        current=_current(precip=3.5, humidity=90.0, wind=15.0),
        forecast=_forecast([1.0, 2.0, 0.0, 4.0]),
        summary=_summary(rainfall_avg=5.0),
        comparison=_comparison(),
        history=_history([10.0, 12.0, 8.0]),
        forecast_hours=24,
    )
    assert features.current_precipitation == 3.5
    assert features.forecast_precipitation == 7.0
    assert features.historical_rainfall_baseline == 5.0
    assert features.humidity == 90.0
    assert features.wind_speed == 15.0
    assert features.recent_rainfall == 30.0
    assert features.precipitation_intensity_indicator == 4.0
    assert features.forecast_daily_equivalent == pytest.approx(7.0)  # 7 * 24/24


def test_rainfall_anomaly_from_forecast_and_baseline():
    # Window sum 24 mm over 24h => daily equivalent 24; baseline 8 => anomaly = 2.0
    features = build_features(
        current=_current(),
        forecast=_forecast([24.0]),
        summary=_summary(rainfall_avg=8.0),
        comparison=None,
        history=None,
        forecast_hours=24,
    )
    assert features.rainfall_anomaly == pytest.approx(2.0)
    assert features.forecast_rainfall_excess == pytest.approx(16.0)


def test_missing_rainfall_data_stays_null():
    features = build_features(
        current=None,
        forecast=None,
        summary=None,
        comparison=None,
        history=None,
        forecast_hours=24,
    )
    assert features.current_precipitation is None
    assert features.forecast_precipitation is None
    assert features.historical_rainfall_baseline is None
    assert features.rainfall_anomaly is None
    assert features.recent_rainfall is None
    assert features.humidity is None
    assert features.wind_speed is None


def test_empty_climate_summary_does_not_invent_baseline():
    features = build_features(
        current=_current(precip=0.0),
        forecast=_forecast([0.0]),
        summary=_summary(rainfall_avg=0.0, observations=0),
        comparison=None,
        history=None,
        forecast_hours=24,
    )
    assert features.historical_rainfall_baseline is None
    assert features.rainfall_anomaly is None


def test_risk_score_bounds():
    model = TransparentRiskModel()
    dry = RiskFeatures(
        current_precipitation=0.0,
        forecast_precipitation=0.0,
        historical_rainfall_baseline=10.0,
        rainfall_anomaly=-0.5,
        recent_rainfall=0.0,
        humidity=40.0,
        wind_speed=5.0,
        forecast_daily_equivalent=0.0,
        forecast_rainfall_excess=-10.0,
        precipitation_persistence=0.0,
        precipitation_intensity_indicator=0.0,
    )
    wet = RiskFeatures(
        current_precipitation=50.0,
        forecast_precipitation=80.0,
        historical_rainfall_baseline=2.0,
        rainfall_anomaly=5.0,
        recent_rainfall=200.0,
        humidity=99.0,
        wind_speed=40.0,
        forecast_daily_equivalent=80.0,
        forecast_rainfall_excess=78.0,
        precipitation_persistence=1.0,
        precipitation_intensity_indicator=20.0,
    )
    empty = RiskFeatures()
    assert 0.0 <= model.calculate_score(dry) <= 1.0
    assert 0.0 <= model.calculate_score(wet) <= 1.0
    assert model.calculate_score(empty) == 0.0
    assert model.calculate_score(wet) > model.calculate_score(dry)


def test_risk_level_classification():
    assert classify_risk_level(0.0) == "LOW"
    assert classify_risk_level(0.24) == "LOW"
    assert classify_risk_level(0.25) == "MODERATE"
    assert classify_risk_level(0.49) == "MODERATE"
    assert classify_risk_level(0.50) == "HIGH"
    assert classify_risk_level(0.74) == "HIGH"
    assert classify_risk_level(0.75) == "EXTREME"
    assert classify_risk_level(1.0) == "EXTREME"


def test_explanation_generation_uses_actual_features():
    features = RiskFeatures(
        current_precipitation=4.0,
        forecast_precipitation=20.0,
        historical_rainfall_baseline=5.0,
        rainfall_anomaly=0.72,
        recent_rainfall=50.0,
        forecast_daily_equivalent=20.0,
        forecast_rainfall_excess=15.0,
        precipitation_persistence=0.8,
        precipitation_intensity_indicator=6.0,
    )
    drivers = build_drivers(features)
    messages = [d.message for d in drivers]
    features_named = [d.feature for d in drivers]
    assert "rainfall_anomaly" in features_named
    assert any("above the historical baseline" in m for m in messages)
    assert any("elevated relative to the historical baseline" in m for m in messages)
    assert any("increased wetness" in m for m in messages)
    assert not any("unrelated" in m.lower() for m in messages)


def test_recommendation_generation():
    assert "Continue normal monitoring." in recommendations_for_level("LOW")
    assert "localized waterlogging" in " ".join(recommendations_for_level("MODERATE"))
    assert "flood-prone" in " ".join(recommendations_for_level("HIGH"))
    assert "official authorities" in " ".join(recommendations_for_level("EXTREME"))


def _patch_upstreams(current, forecast, summary=None, comparison=None, history=None):
    summary = summary or _summary()
    comparison = comparison or _comparison()
    history = history or _history([2.0, 3.0])
    return (
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_current_weather",
            new=AsyncMock(return_value=current),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_forecast",
            new=AsyncMock(return_value=forecast),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_summary",
            new=AsyncMock(return_value=summary),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_comparison",
            new=AsyncMock(return_value=comparison),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_history",
            new=AsyncMock(return_value=history),
        ),
    )


def test_risk_api_valid_coordinates():
    patches = _patch_upstreams(_current(), _forecast([1.0, 2.0, 3.0]))
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        res = client.get("/api/v1/risk/assess?lat=12.8342&lon=79.7036&forecast_hours=24")
    assert res.status_code == 200
    body = res.json()
    assert body["hazard"] == "heavy_rain_flood"
    assert body["risk_level"] in {"LOW", "MODERATE", "HIGH", "EXTREME"}
    assert 0.0 <= body["risk_score"] <= 1.0
    assert body["forecast_window_hours"] == 24
    assert body["model"]["name"] == "WeatherGPT Transparent Risk Model"
    assert body["model"]["version"] == "0.1"
    assert body["model"]["type"] == "rule_based_prototype"
    assert "features" in body
    assert "drivers" in body
    assert "recommended_actions" in body
    assert body["features"]["current_precipitation"] == 2.0
    assert body["location"]["latitude"] == 12.8342


def test_risk_api_invalid_latitude():
    res = client.get("/api/v1/risk/assess?lat=95.0&lon=79.7036")
    assert res.status_code == 400
    assert "Latitude" in res.json()["detail"]


def test_risk_api_invalid_longitude():
    res = client.get("/api/v1/risk/assess?lat=12.8342&lon=200.0")
    assert res.status_code == 400
    assert "Longitude" in res.json()["detail"]


def test_risk_api_invalid_forecast_hours():
    res = client.get("/api/v1/risk/assess?lat=12.8342&lon=79.7036&forecast_hours=0")
    assert res.status_code == 400
    assert "forecast_hours" in res.json()["detail"]


def test_risk_api_weather_and_climate_mocked():
    current = _current(precip=1.2)
    forecast = _forecast([0.5, 0.5])
    patches = _patch_upstreams(current, forecast, summary=_summary(rainfall_avg=4.0))
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        res = client.get("/api/v1/risk/assess?lat=12.8342&lon=79.7036")
    assert res.status_code == 200
    assert res.json()["features"]["historical_rainfall_baseline"] == 4.0


def test_risk_api_partial_climate_failure_still_returns():
    patches = (
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_current_weather",
            new=AsyncMock(return_value=_current()),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_forecast",
            new=AsyncMock(return_value=_forecast([1.0])),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_summary",
            new=AsyncMock(side_effect=ProviderApiError("archive down")),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_comparison",
            new=AsyncMock(side_effect=ProviderApiError("archive down")),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.climate_service.get_history",
            new=AsyncMock(side_effect=ProviderApiError("archive down")),
        ),
    )
    with patches[0], patches[1], patches[2], patches[3], patches[4]:
        res = client.get("/api/v1/risk/assess?lat=12.8342&lon=79.7036")
    assert res.status_code == 200
    assert res.json()["features"]["historical_rainfall_baseline"] is None
    assert res.json()["features"]["current_precipitation"] == 2.0


def test_risk_api_both_weather_sources_unavailable():
    patches = (
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_current_weather",
            new=AsyncMock(side_effect=ProviderApiError("current down")),
        ),
        patch(
            "app.api.v1.endpoints.risk.risk_service.weather_service.get_forecast",
            new=AsyncMock(side_effect=ProviderApiError("forecast down")),
        ),
    )
    with patches[0], patches[1]:
        res = client.get("/api/v1/risk/assess?lat=12.8342&lon=79.7036")
    assert res.status_code == 503
