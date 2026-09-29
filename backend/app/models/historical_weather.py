from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from app.core.database import Base


class HistoricalWeather(Base):
    """
    SQLAlchemy ORM Model for Historical Weather Telemetry Records.
    Stores observed past weather data indexed by location coordinates and timestamp.
    """

    __tablename__ = "historical_weather"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    latitude = Column(Float, nullable=False, index=True)
    longitude = Column(Float, nullable=False, index=True)
    timestamp = Column(DateTime, nullable=False, index=True)

    temperature = Column(Float, nullable=False)
    feels_like = Column(Float, nullable=True)
    humidity = Column(Float, nullable=False)
    pressure = Column(Float, nullable=False)
    precipitation = Column(Float, nullable=False, default=0.0)
    wind_speed = Column(Float, nullable=False, default=0.0)
    wind_direction = Column(Float, nullable=False, default=0.0)

    condition = Column(String(100), nullable=False, default="Clear")
    data_source = Column(String(100), nullable=False, default="Historical Archive")

    __table_args__ = (
        Index("idx_lat_lon_timestamp", "latitude", "longitude", "timestamp"),
    )
