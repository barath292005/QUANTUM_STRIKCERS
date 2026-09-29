import time
import threading
from typing import Any, Dict, Optional, Tuple


class WeatherCache:
    """
    In-memory thread-safe TTL cache for weather queries.
    Prevents redundant external API calls for close coordinate locations.
    """

    def __init__(self, default_ttl: int = 300):
        self.default_ttl = default_ttl
        self._cache: Dict[str, Tuple[float, Any]] = {}
        self._lock = threading.Lock()

    def _make_key(self, prefix: str, lat: float, lon: float) -> str:
        # Key rounded to 3 decimal places (~100m grid resolution)
        return f"{prefix}:{round(lat, 3)}:{round(lon, 3)}"

    def get(self, prefix: str, lat: float, lon: float) -> Optional[Any]:
        key = self._make_key(prefix, lat, lon)
        with self._lock:
            if key in self._cache:
                timestamp, data = self._cache[key]
                if time.time() - timestamp < self.default_ttl:
                    return data
                # Expired
                del self._cache[key]
        return None

    def set(self, prefix: str, lat: float, lon: float, data: Any, ttl: Optional[int] = None) -> None:
        key = self._make_key(prefix, lat, lon)
        effective_ttl = ttl if ttl is not None else self.default_ttl
        with self._lock:
            self._cache[key] = (time.time(), data)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


weather_cache = WeatherCache(default_ttl=300)
