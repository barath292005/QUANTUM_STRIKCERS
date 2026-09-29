"""Transparent rule-based scoring and classification.

WeatherGPT Transparent Risk Model v0.1 is an engineering prototype.
Weights and bins are configurable in thresholds.py and are NOT a trained
machine-learning model and NOT official warning criteria.
"""

from __future__ import annotations

import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

from app.services.risk.schemas import RiskFeatures
from app.services.risk.thresholds import (
    ANOMALY_SATURATION_RATIO,
    CURRENT_PRECIP_SATURATION_MM,
    FORECAST_DAILY_SATURATION_MM,
    RECENT_RAINFALL_SATURATION_MM,
    RISK_LEVEL_THRESHOLDS,
    SCORE_WEIGHTS,
)

logger = logging.getLogger(__name__)


def _clamp01(value: float) -> float:
    return max(0.0, min(1.0, value))


def _saturate(raw: Optional[float], cap: float) -> Optional[float]:
    """Map a non-negative quantity onto [0, 1] using a linear saturation cap."""
    if raw is None or cap <= 0:
        return None
    return _clamp01(raw / cap)


class HazardRiskModel(ABC):
    """Swap-point for a future ML flood model without changing the API contract.

    Later implementations (e.g. MLFloodRiskModel) should implement the same
    three methods so RiskService, RiskResponse, and RiskPanel stay stable.
    """

    @abstractmethod
    def calculate_score(self, features: RiskFeatures) -> float:
        """Return a composite score in [0.0, 1.0]."""

    @abstractmethod
    def predict(self, features: RiskFeatures) -> Tuple[float, str]:
        """Return (score, risk_level)."""

    @abstractmethod
    def explain(self, features: RiskFeatures) -> Dict[str, Optional[float]]:
        """Return the component scores used (for logging / downstream explainers)."""


def classify_risk_level(score: float) -> str:
    """Map a [0, 1] score onto LOW / MODERATE / HIGH / EXTREME.

    Bins are initial configurable engineering thresholds for prototype
    decision support, not official IMD or hydrological warning thresholds.
    """
    bounded = _clamp01(score)
    for level, (lo, hi) in RISK_LEVEL_THRESHOLDS.items():
        if lo <= bounded < hi:
            return level
    return "EXTREME"


def recommendations_for_level(level: str) -> List[str]:
    """Return actions proportional to the prototype risk level.

    These are generic preparedness prompts, not emergency declarations.
    """
    mapping = {
        "LOW": [
            "Continue normal monitoring.",
        ],
        "MODERATE": [
            "Monitor official weather updates.",
            "Be aware of localized waterlogging.",
        ],
        "HIGH": [
            "Monitor official weather alerts.",
            "Avoid unnecessary travel through known flood-prone areas.",
            "Prepare for possible waterlogging.",
        ],
        "EXTREME": [
            "Follow instructions from official authorities.",
            "Avoid flood-prone areas.",
            "Seek local emergency guidance when applicable.",
        ],
    }
    return list(mapping.get(level, mapping["LOW"]))


class TransparentRiskModel(HazardRiskModel):
    """Rule-based prototype. Not a trained ML model."""

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        self.weights = dict(weights or SCORE_WEIGHTS)

    def _component_scores(self, features: RiskFeatures) -> Dict[str, Optional[float]]:
        """Build named component scores; None means the component is unavailable.

        rain_score:
            saturate(current_precipitation / CURRENT_PRECIP_SATURATION_MM)
            If current precip is missing, use recent_rainfall against
            RECENT_RAINFALL_SATURATION_MM as a wetness proxy.

        forecast_score:
            Convert window sum to a daily equivalent F * (24 / H) using
            forecast_precipitation when the caller stored the window sum, then
            saturate against FORECAST_DAILY_SATURATION_MM. The daily equivalent
            is reconstructed only if forecast_rainfall_excess + baseline exist;
            otherwise saturate the raw window sum against the same daily cap
            (conservative if the window is shorter than 24h).

        anomaly_score:
            saturate(max(rainfall_anomaly, 0) / ANOMALY_SATURATION_RATIO)
            Negative anomalies contribute 0 (they do not increase this component).

        persistence_score:
            precipitation_persistence already in [0, 1].
        """
        rain_score = _saturate(features.current_precipitation, CURRENT_PRECIP_SATURATION_MM)
        if rain_score is None:
            rain_score = _saturate(features.recent_rainfall, RECENT_RAINFALL_SATURATION_MM)

        daily_forecast = features.forecast_daily_equivalent
        if daily_forecast is None:
            daily_forecast = features.forecast_precipitation
        forecast_score = _saturate(daily_forecast, FORECAST_DAILY_SATURATION_MM)

        if features.rainfall_anomaly is None:
            anomaly_score = None
        else:
            anomaly_score = _saturate(max(features.rainfall_anomaly, 0.0), ANOMALY_SATURATION_RATIO)

        persistence_score = None
        if features.precipitation_persistence is not None:
            persistence_score = _clamp01(features.precipitation_persistence)

        return {
            "rain_score": rain_score,
            "forecast_score": forecast_score,
            "anomaly_score": anomaly_score,
            "persistence_score": persistence_score,
        }

    def calculate_score(self, features: RiskFeatures) -> float:
        components = self._component_scores(features)
        available = {k: v for k, v in components.items() if v is not None}
        if not available:
            logger.info("risk_calculation", extra={"score": 0.0, "reason": "no_components"})
            return 0.0

        weight_sum = sum(self.weights.get(k, 0.0) for k in available)
        if weight_sum <= 0:
            # Equal blend if configured weights were all zero for available keys.
            score = sum(available.values()) / len(available)
        else:
            score = sum(available[k] * self.weights.get(k, 0.0) for k in available) / weight_sum

        score = round(_clamp01(score), 4)
        logger.info(
            "risk_calculation",
            extra={"score": score, "components": {k: available[k] for k in available}},
        )
        return score

    def predict(self, features: RiskFeatures) -> Tuple[float, str]:
        score = self.calculate_score(features)
        level = classify_risk_level(score)
        logger.info("risk_classification", extra={"score": score, "risk_level": level})
        return score, level

    def explain(self, features: RiskFeatures) -> Dict[str, Optional[float]]:
        return self._component_scores(features)
