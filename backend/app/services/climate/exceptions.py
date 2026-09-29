from app.services.weather.exceptions import WeatherServiceError


class ClimateServiceError(WeatherServiceError):
    """Base exception for climate analysis domain errors."""
    pass


class InvalidDateRangeError(ClimateServiceError):
    """Raised when start_date or end_date is malformed or start_date > end_date."""
    pass


class InsufficientDataError(ClimateServiceError):
    """Raised when historical observations count is insufficient for statistical calculations."""
    pass
