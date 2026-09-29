class WeatherServiceError(Exception):
    """Base exception for all weather service operations."""
    pass


class InvalidCoordinatesError(WeatherServiceError):
    """Raised when provided latitude or longitude values are invalid or out of range."""
    pass


class ProviderConfigError(WeatherServiceError):
    """Raised when weather provider configuration or API credentials are missing."""
    pass


class ProviderTimeoutError(WeatherServiceError):
    """Raised when external weather API request times out."""
    pass


class ProviderApiError(WeatherServiceError):
    """Raised when external provider returns HTTP error or unparseable payload."""
    def __init__(self, message: str, status_code: int = 502):
        super().__init__(message)
        self.status_code = status_code
