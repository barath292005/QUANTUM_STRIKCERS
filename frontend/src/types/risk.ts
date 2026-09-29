export interface RiskFeatures {
  current_precipitation: number | null;
  forecast_precipitation: number | null;
  historical_rainfall_baseline: number | null;
  rainfall_anomaly: number | null;
  recent_rainfall: number | null;
  humidity: number | null;
  wind_speed: number | null;
  forecast_daily_equivalent?: number | null;
  forecast_rainfall_excess?: number | null;
  precipitation_persistence?: number | null;
  precipitation_intensity_indicator?: number | null;
}

export interface RiskDriver {
  feature: string;
  value: number | null;
  direction: string;
  message: string;
}

export interface RiskAssessment {
  hazard: string;
  risk_level: string;
  risk_score: number;
  forecast_window_hours: number;
  features: RiskFeatures;
  drivers: RiskDriver[];
  recommended_actions: string[];
  model: {
    name: string;
    version: string;
    type: string;
  };
  limitations: string[];
}

export const RISK_LEVELS = ['LOW', 'MODERATE', 'HIGH', 'EXTREME'] as const;
export type RiskLevel = (typeof RISK_LEVELS)[number];

export function isRiskLevel(value: string | undefined | null): value is RiskLevel {
  return value === 'LOW' || value === 'MODERATE' || value === 'HIGH' || value === 'EXTREME';
}

export function formatHazardLabel(hazard: string | undefined | null): string {
  if (!hazard) return '—';
  if (hazard === 'heavy_rain_flood') return 'Heavy Rain / Flood Risk';
  return hazard.replace(/_/g, ' ');
}

export function formatCoordinates(lat: number, lon: number): string {
  const ns = lat >= 0 ? 'N' : 'S';
  const ew = lon >= 0 ? 'E' : 'W';
  return `${Math.abs(lat).toFixed(4)}° ${ns}, ${Math.abs(lon).toFixed(4)}° ${ew}`;
}

export function formatRiskScorePercent(score: number | null | undefined): string | null {
  if (score === null || score === undefined || Number.isNaN(score)) return null;
  return `${Math.round(score * 100)}%`;
}
