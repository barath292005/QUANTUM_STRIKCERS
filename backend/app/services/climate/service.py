from datetime import datetime, date, timedelta
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.historical_weather import HistoricalWeather
from app.services.weather.schemas import Location
from app.services.weather.service import WeatherService
from app.services.weather.exceptions import InvalidCoordinatesError
from app.services.climate.provider import BaseHistoricalProvider
from app.services.climate.providers.openmeteo_archive import OpenMeteoArchiveProvider
from app.services.climate.schemas import (
    HistoricalObservationItem,
    HistoricalDataResponse,
    ClimateSummaryResponse,
    ClimateComparisonResponse,
    ClimateTrendResponse,
)
from app.services.climate.exceptions import InvalidDateRangeError
from app.services.climate.analytics import (
    calculate_summary,
    calculate_comparison_metric,
    calculate_trend,
)


class ClimateService:
    """
    Main Domain Orchestrator for Historical Climate Data & Statistical Analysis.
    Manages database persistence, archive API provider ingestion, and analytics calculations.
    """

    def __init__(self, provider: Optional[BaseHistoricalProvider] = None):
        self.provider = provider or OpenMeteoArchiveProvider()
        self.weather_service = WeatherService()

    def _validate_inputs(self, lat: float, lon: float, start_date_str: str, end_date_str: str) -> tuple[date, date]:
        if not (-90.0 <= lat <= 90.0):
            raise InvalidCoordinatesError(f"Latitude {lat} must be between -90 and 90 degrees.")
        if not (-180.0 <= lon <= 180.0):
            raise InvalidCoordinatesError(f"Longitude {lon} must be between -180 and 180 degrees.")

        try:
            d_start = datetime.strptime(start_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateRangeError(f"Invalid start_date '{start_date_str}'. Expected format YYYY-MM-DD.")

        try:
            d_end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateRangeError(f"Invalid end_date '{end_date_str}'. Expected format YYYY-MM-DD.")

        if d_start > d_end:
            raise InvalidDateRangeError(f"start_date ({start_date_str}) cannot be later than end_date ({end_date_str}).")

        return d_start, d_end

    async def get_history(
        self, lat: float, lon: float, start_date_str: str, end_date_str: str, db: Session
    ) -> HistoricalDataResponse:
        d_start, d_end = self._validate_inputs(lat, lon, start_date_str, end_date_str)
        rounded_lat = round(lat, 4)
        rounded_lon = round(lon, 4)

        # Convert to datetime bounds
        dt_start = datetime.combine(d_start, datetime.min.time())
        dt_end = datetime.combine(d_end, datetime.max.time())

        # Query database for existing records
        existing_models = (
            db.query(HistoricalWeather)
            .filter(
                HistoricalWeather.latitude == rounded_lat,
                HistoricalWeather.longitude == rounded_lon,
                HistoricalWeather.timestamp >= dt_start,
                HistoricalWeather.timestamp <= dt_end,
            )
            .order_by(HistoricalWeather.timestamp.asc())
            .all()
        )

        records: List[HistoricalObservationItem] = []
        if existing_models and len(existing_models) > 0:
            for m in existing_models:
                records.append(
                    HistoricalObservationItem(
                        timestamp=m.timestamp.isoformat(),
                        temperature=m.temperature,
                        feels_like=m.feels_like,
                        humidity=m.humidity,
                        pressure=m.pressure,
                        precipitation=m.precipitation,
                        wind_speed=m.wind_speed,
                        wind_direction=m.wind_direction,
                        condition=m.condition,
                        data_source=m.data_source,
                    )
                )
        else:
            # Fetch from archive provider if not in database
            fetched = await self.provider.fetch_historical_observations(rounded_lat, rounded_lon, d_start, d_end)
            records = fetched

            # Persist fetched records into database
            db_models = []
            for item in fetched:
                dt_obj = datetime.fromisoformat(item.timestamp.replace("Z", "+00:00"))
                db_models.append(
                    HistoricalWeather(
                        latitude=rounded_lat,
                        longitude=rounded_lon,
                        timestamp=dt_obj,
                        temperature=item.temperature,
                        feels_like=item.feels_like,
                        humidity=item.humidity,
                        pressure=item.pressure,
                        precipitation=item.precipitation,
                        wind_speed=item.wind_speed,
                        wind_direction=item.wind_direction,
                        condition=item.condition,
                        data_source=item.data_source,
                    )
                )

            if db_models:
                try:
                    db.bulk_save_objects(db_models)
                    db.commit()
                except Exception as e:
                    db.rollback()
                    # Log silently or ignore DB write errors to avoid failing the query
                    print(f"Warning: Failed to save historical records to DB: {e}")

        location_obj = Location(latitude=rounded_lat, longitude=rounded_lon)
        return HistoricalDataResponse(
            location=location_obj,
            start_date=start_date_str,
            end_date=end_date_str,
            total_records=len(records),
            records=records,
        )

    async def get_summary(
        self, lat: float, lon: float, start_date_str: str, end_date_str: str, db: Session
    ) -> ClimateSummaryResponse:
        history_res = await self.get_history(lat, lon, start_date_str, end_date_str, db)
        return calculate_summary(history_res.records, history_res.location, start_date_str, end_date_str)

    async def get_comparison(
        self, lat: float, lon: float, target_date_str: str, db: Session
    ) -> ClimateComparisonResponse:
        # Fetch current real-time weather
        current_res = await self.weather_service.get_current_weather(lat, lon)
        current_temp = current_res.current.temperature
        current_precip = current_res.current.precipitation

        # Target date & 30-day baseline historical query
        try:
            d_target = datetime.strptime(target_date_str, "%Y-%m-%d").date()
        except ValueError:
            raise InvalidDateRangeError(f"Invalid date '{target_date_str}'. Expected format YYYY-MM-DD.")

        d_start = d_target - timedelta(days=30)
        history_res = await self.get_history(lat, lon, d_start.isoformat(), d_target.isoformat(), db)

        summary = calculate_summary(history_res.records, history_res.location, d_start.isoformat(), d_target.isoformat())

        temp_metric = calculate_comparison_metric(current_temp, summary.temp_avg, is_rainfall=False)
        rainfall_metric = calculate_comparison_metric(current_precip, summary.rainfall_avg, is_rainfall=True)

        return ClimateComparisonResponse(
            location=history_res.location,
            target_date=target_date_str,
            temperature=temp_metric,
            rainfall=rainfall_metric,
        )

    async def get_trend(
        self, lat: float, lon: float, start_date_str: str, end_date_str: str, variable: str, db: Session
    ) -> ClimateTrendResponse:
        history_res = await self.get_history(lat, lon, start_date_str, end_date_str, db)
        return calculate_trend(history_res.records, history_res.location, variable, start_date_str, end_date_str)
