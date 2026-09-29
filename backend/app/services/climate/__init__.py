"""
Climate Analysis & Historical Telemetry Package for WeatherGPT.
"""

from app.services.climate.service import ClimateService
from app.services.climate.provider import BaseHistoricalProvider
from app.services.climate.schemas import (
    HistoricalObservationItem,
    HistoricalDataResponse,
    ClimateSummaryResponse,
    ClimateComparisonResponse,
    ClimateTrendResponse,
)
from app.services.climate.exceptions import (
    ClimateServiceError,
    InvalidDateRangeError,
    InsufficientDataError,
)

__all__ = [
    "ClimateService",
    "BaseHistoricalProvider",
    "HistoricalObservationItem",
    "HistoricalDataResponse",
    "ClimateSummaryResponse",
    "ClimateComparisonResponse",
    "ClimateTrendResponse",
    "ClimateServiceError",
    "InvalidDateRangeError",
    "InsufficientDataError",
]
