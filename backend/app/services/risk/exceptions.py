from app.services.weather.exceptions import WeatherServiceError


class RiskServiceError(WeatherServiceError):
    """Base exception for impact-based risk assessment domain errors."""


class InsufficientRiskInputsError(RiskServiceError):
    """Raised when neither current weather nor forecast data is available."""


class InvalidForecastWindowError(RiskServiceError):
    """Raised when forecast_hours is outside the allowed engineering range."""
