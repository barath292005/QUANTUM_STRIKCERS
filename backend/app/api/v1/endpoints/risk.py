from fastapi import APIRouter, Query, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.risk.service import RiskService
from app.services.risk.schemas import RiskResponse
from app.services.risk.exceptions import InsufficientRiskInputsError, InvalidForecastWindowError, RiskServiceError
from app.services.weather.exceptions import InvalidCoordinatesError, ProviderApiError, ProviderTimeoutError, ProviderConfigError
from app.services.climate.exceptions import ClimateServiceError

router = APIRouter()
risk_service = RiskService()


@router.get("/assess", response_model=RiskResponse, summary="Assess Heavy Rain / Flood-Related Risk Indicators")
async def assess_risk(
    lat: float = Query(..., description="Latitude coordinate (-90.0 to 90.0)"),
    lon: float = Query(..., description="Longitude coordinate (-180.0 to 180.0)"),
    forecast_hours: int = Query(24, description="Forecast window in hours (1 to 168)"),
    db: Session = Depends(get_db),
) -> RiskResponse:
    """
    Prototype heavy-rain / flood-related risk assessment.

    Combines WeatherService (current + forecast) and ClimateService (baseline,
    comparison, recent history) into a transparent engineering score.
    This is decision-support only and is not an official warning.
    """
    try:
        return await risk_service.assess(lat, lon, forecast_hours, db)
    except InvalidCoordinatesError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InvalidForecastWindowError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except InsufficientRiskInputsError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ProviderConfigError as e:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(e))
    except ProviderTimeoutError as e:
        raise HTTPException(status_code=status.HTTP_504_GATEWAY_TIMEOUT, detail=str(e))
    except ProviderApiError as e:
        raise HTTPException(status_code=e.status_code, detail=str(e))
    except ClimateServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
    except RiskServiceError as e:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(e))
