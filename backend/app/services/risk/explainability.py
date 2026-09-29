"""Explanations grounded only in calculated feature values."""

from __future__ import annotations

from typing import List

from app.services.risk.schemas import RiskDriver, RiskFeatures
from app.services.risk.thresholds import WET_STEP_PRECIP_MM


def build_drivers(features: RiskFeatures) -> List[RiskDriver]:
    """Emit drivers only when the corresponding feature is present and informative."""
    drivers: List[RiskDriver] = []

    if features.forecast_precipitation is not None:
        if features.historical_rainfall_baseline is not None and features.forecast_rainfall_excess is not None:
            if features.forecast_rainfall_excess > 0:
                drivers.append(
                    RiskDriver(
                        feature="forecast_precipitation",
                        value=features.forecast_precipitation,
                        direction="increases_risk",
                        message="Forecast rainfall is elevated relative to the historical baseline.",
                    )
                )
            elif features.forecast_rainfall_excess < 0 and features.forecast_precipitation > 0:
                drivers.append(
                    RiskDriver(
                        feature="forecast_precipitation",
                        value=features.forecast_precipitation,
                        direction="decreases_risk",
                        message="Forecast rainfall is present but below the historical daily baseline.",
                    )
                )
            elif features.forecast_precipitation <= 0:
                drivers.append(
                    RiskDriver(
                        feature="forecast_precipitation",
                        value=features.forecast_precipitation,
                        direction="decreases_risk",
                        message="No rainfall is indicated in the forecast window.",
                    )
                )
        elif features.forecast_precipitation > 0:
            drivers.append(
                RiskDriver(
                    feature="forecast_precipitation",
                    value=features.forecast_precipitation,
                    direction="increases_risk",
                    message="Forecast rainfall is present in the assessment window.",
                )
            )
        else:
            drivers.append(
                RiskDriver(
                    feature="forecast_precipitation",
                    value=features.forecast_precipitation,
                    direction="decreases_risk",
                    message="No rainfall is indicated in the forecast window.",
                )
            )

    if features.rainfall_anomaly is not None:
        if features.rainfall_anomaly > 0:
            magnitude = "substantially " if features.rainfall_anomaly >= 0.5 else ""
            drivers.append(
                RiskDriver(
                    feature="rainfall_anomaly",
                    value=features.rainfall_anomaly,
                    direction="increases_risk",
                    message=f"Rainfall is {magnitude}above the historical baseline.",
                )
            )
        elif features.rainfall_anomaly < 0:
            drivers.append(
                RiskDriver(
                    feature="rainfall_anomaly",
                    value=features.rainfall_anomaly,
                    direction="decreases_risk",
                    message="Rainfall is below the historical baseline.",
                )
            )

    if features.recent_rainfall is not None:
        baseline = features.historical_rainfall_baseline
        # Compare 7-day accumulation to ~7 × daily baseline when baseline exists.
        if baseline is not None and baseline > 0:
            expected = baseline * 7.0
            if features.recent_rainfall > expected:
                drivers.append(
                    RiskDriver(
                        feature="recent_rainfall",
                        value=features.recent_rainfall,
                        direction="increases_risk",
                        message="Recent rainfall indicates increased wetness.",
                    )
                )
            elif features.recent_rainfall > 0:
                drivers.append(
                    RiskDriver(
                        feature="recent_rainfall",
                        value=features.recent_rainfall,
                        direction="decreases_risk",
                        message="Recent rainfall is below the 7-day historical daily baseline accumulation.",
                    )
                )
        elif features.recent_rainfall > 0:
            drivers.append(
                RiskDriver(
                    feature="recent_rainfall",
                    value=features.recent_rainfall,
                    direction="increases_risk",
                    message="Recent rainfall indicates increased wetness.",
                )
            )

    if features.current_precipitation is not None:
        if features.current_precipitation > WET_STEP_PRECIP_MM:
            drivers.append(
                RiskDriver(
                    feature="current_precipitation",
                    value=features.current_precipitation,
                    direction="increases_risk",
                    message="Current precipitation is contributing rainfall at the observation time.",
                )
            )
        else:
            drivers.append(
                RiskDriver(
                    feature="current_precipitation",
                    value=features.current_precipitation,
                    direction="decreases_risk",
                    message="Little or no precipitation is occurring at the observation time.",
                )
            )

    if features.precipitation_persistence is not None:
        if features.precipitation_persistence >= 0.5:
            drivers.append(
                RiskDriver(
                    feature="precipitation_persistence",
                    value=features.precipitation_persistence,
                    direction="increases_risk",
                    message="Rainfall persists across a large fraction of the forecast window.",
                )
            )
        elif features.precipitation_persistence > 0:
            drivers.append(
                RiskDriver(
                    feature="precipitation_persistence",
                    value=features.precipitation_persistence,
                    direction="decreases_risk",
                    message="Rainfall is intermittent rather than persistent in the forecast window.",
                )
            )

    if features.precipitation_intensity_indicator is not None and features.precipitation_intensity_indicator > 5.0:
        drivers.append(
            RiskDriver(
                feature="precipitation_intensity_indicator",
                value=features.precipitation_intensity_indicator,
                direction="increases_risk",
                message="Peak forecast precipitation intensity is elevated within the window.",
            )
        )

    return drivers
