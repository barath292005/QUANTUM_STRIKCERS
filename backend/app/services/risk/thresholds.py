"""
Configurable engineering thresholds for WeatherGPT Transparent Risk Model v0.1.

These values are INITIAL CONFIGURABLE ENGINEERING THRESHOLDS for prototype
decision support. They are NOT official IMD, government, or hydrological
warning thresholds, and they are NOT scientifically validated flood criteria.
"""

# Forecast window bounds for GET /api/v1/risk/assess
FORECAST_HOURS_MIN = 1
FORECAST_HOURS_MAX = 168  # 7 days

# Climate lookback used to estimate a daily rainfall baseline (mm/day).
CLIMATE_BASELINE_DAYS = 30

# Lookback used to accumulate "recent rainfall" from historical observations.
RECENT_RAINFALL_DAYS = 7

# Trace precipitation (mm) used to count a forecast step as "wet".
WET_STEP_PRECIP_MM = 0.1

# Saturation caps used only to map raw millimetres onto [0, 1] score components.
# These are engineering saturations, not physical flood thresholds.
CURRENT_PRECIP_SATURATION_MM = 20.0
FORECAST_DAILY_SATURATION_MM = 50.0
RECENT_RAINFALL_SATURATION_MM = 100.0
ANOMALY_SATURATION_RATIO = 2.0  # |anomaly ratio| of 2.0 maps to 1.0
INTENSITY_SATURATION_MM = 15.0  # max hourly (or step) precip saturation

# Composite score weights. Missing components are dropped and remaining
# weights are renormalized so the composite stays in [0, 1].
SCORE_WEIGHTS = {
    "rain_score": 0.20,
    "forecast_score": 0.35,
    "anomaly_score": 0.25,
    "persistence_score": 0.20,
}

# Inclusive lower bound, exclusive upper bound except EXTREME which includes 1.0.
# Prototype decision-support bins only.
RISK_LEVEL_THRESHOLDS = {
    "LOW": (0.0, 0.25),
    "MODERATE": (0.25, 0.50),
    "HIGH": (0.50, 0.75),
    "EXTREME": (0.75, 1.01),
}

MODEL_NAME = "WeatherGPT Transparent Risk Model"
MODEL_VERSION = "0.1"
MODEL_TYPE = "rule_based_prototype"

HAZARD_ID = "heavy_rain_flood"

LIMITATIONS = [
    "Prototype decision-support assessment.",
    "Not an official warning.",
    "Requires validation against historical flood observations for production use.",
    "Meteorological and climate indicators do not by themselves predict that a flood will occur.",
]
