from abc import ABC, abstractmethod
from typing import List
from datetime import date
from app.services.climate.schemas import HistoricalObservationItem


class BaseHistoricalProvider(ABC):
    """
    Abstract Base Class for historical meteorological data ingestion.
    """

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """String name identifier for historical data provider."""
        pass

    @abstractmethod
    async def fetch_historical_observations(
        self, lat: float, lon: float, start_date: date, end_date: date
    ) -> List[HistoricalObservationItem]:
        """Fetches and normalizes historical observations from external archive provider."""
        pass
