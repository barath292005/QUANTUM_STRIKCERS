from datetime import date
from typing import Optional
from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db, engine, Base
from app.services.climate.service import ClimateService
from app.services.climate.schemas import (
    HistoricalDataResponse,
    ClimateSummaryResponse,
    ClimateComparisonResponse,
    ClimateTrendResponse,
)
from app.services.climate.exceptions import (
    InvalidDateRangeError,
    InsufficientDataError,
    ClimateServiceError,
)
from app.services.weather.exceptions import InvalidCoordinatesError, ProviderApiError, ProviderTimeoutError

# Ensure tables are created on database startup
Base.metadata.create_all(bind=engine)

router = APIRouter()
climate_service = ClimateService()


@router.get("/history", response_model=HistoricalDataResponse, summary="Get Historical Weather Observations")
async def get_historical_data(
    lat: float = Query(..., description="Latitude coordinate (-90 to 90)"),
    lon: float = Query(..., description="Longitude coordinate (-180 to 180)"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> HistoricalDataResponse:
    try:
        return await climate_service.get_history(lat, lon, start_date, end_date, db)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ClimateServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/summary", response_model=ClimateSummaryResponse, summary="Get Historical Climate Summary")
async def get_climate_summary(
    lat: float = Query(..., description="Latitude coordinate (-90 to 90)"),
    lon: float = Query(..., description="Longitude coordinate (-180 to 180)"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
) -> ClimateSummaryResponse:
    try:
        return await climate_service.get_summary(lat, lon, start_date, end_date, db)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ClimateServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/comparison", response_model=ClimateComparisonResponse, summary="Compare Current Weather vs Historical Baseline")
async def get_climate_comparison(
    lat: float = Query(..., description="Latitude coordinate (-90 to 90)"),
    lon: float = Query(..., description="Longitude coordinate (-180 to 180)"),
    date: Optional[str] = Query(None, description="Target comparison date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db),
) -> ClimateComparisonResponse:
    target_date_str = date or date.today().isoformat()
    try:
        return await climate_service.get_comparison(lat, lon, target_date_str, db)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ClimateServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))


@router.get("/trend", response_model=ClimateTrendResponse, summary="Calculate Linear Climate Trend")
async def get_climate_trend(
    lat: float = Query(..., description="Latitude coordinate (-90 to 90)"),
    lon: float = Query(..., description="Longitude coordinate (-180 to 180)"),
    start_date: str = Query(..., description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(..., description="End date (YYYY-MM-DD)"),
    variable: str = Query("temperature", description="Variable to analyze: 'temperature' or 'precipitation'"),
    db: Session = Depends(get_db),
) -> ClimateTrendResponse:
    try:
        return await climate_service.get_trend(lat, lon, start_date, end_date, variable, db)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidDateRangeError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ClimateServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
