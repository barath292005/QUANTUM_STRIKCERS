import React from 'react';
import {
  ShieldAlert,
  Waves,
  CloudRain,
  Droplets,
  TrendingUp,
  Clock,
  Cpu,
  AlertCircle,
  RefreshCw,
  Info,
} from 'lucide-react';
import type { RiskAssessment } from '../types/risk';
import { formatHazardLabel } from '../types/risk';

interface RiskPanelProps {
  data: RiskAssessment | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

const levelStyles: Record<string, { badge: string; score: string; label: string }> = {
  LOW: {
    badge: 'bg-emerald-950/60 text-emerald-300 border-emerald-800/50',
    score: 'text-emerald-300',
    label: 'LOW',
  },
  MODERATE: {
    badge: 'bg-amber-950/60 text-amber-300 border-amber-800/50',
    score: 'text-amber-300',
    label: 'MODERATE',
  },
  HIGH: {
    badge: 'bg-orange-950/60 text-orange-300 border-orange-800/50',
    score: 'text-orange-300',
    label: 'HIGH',
  },
  EXTREME: {
    badge: 'bg-rose-950/60 text-rose-300 border-rose-800/50',
    score: 'text-rose-300',
    label: 'EXTREME',
  },
};

const formatMm = (value: number | null | undefined) =>
  value === null || value === undefined ? '—' : `${value.toFixed(1)} mm`;

const formatPct = (ratio: number | null | undefined) => {
  if (ratio === null || ratio === undefined) return '—';
  const pct = ratio * 100;
  const sign = pct > 0 ? '+' : '';
  return `${sign}${pct.toFixed(0)}%`;
};

export const RiskPanel: React.FC<RiskPanelProps> = ({ data, loading, error, onRetry }) => {
  const styles = data ? levelStyles[data.risk_level] || levelStyles.LOW : null;
  const scorePct = data ? Math.round(data.risk_score * 100) : null;

  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <ShieldAlert className="w-5 h-5 text-rose-500" />
          <div>
            <h3 className="text-base font-semibold text-slate-100">Impact-Based Risk Analytics</h3>
            <p className="text-xs text-slate-400">Heavy-rain / flood risk assessment from weather + climate indicators</p>
          </div>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-md bg-rose-950/50 text-rose-300 font-mono border border-rose-800/40">
          Prototype
        </span>
      </div>

      {loading && (
        <div className="py-10 flex flex-col items-center justify-center space-y-3 bg-slate-950/50 rounded-lg border border-slate-800/80">
          <RefreshCw className="w-8 h-8 text-rose-400 animate-spin" />
          <div className="text-sm font-medium text-slate-200">Assessing heavy-rain / flood-related indicators...</div>
        </div>
      )}

      {!loading && error && (
        <div className="p-4 bg-rose-950/40 border border-rose-800/60 rounded-lg space-y-2">
          <div className="flex items-center space-x-2 text-rose-300 text-xs">
            <AlertCircle className="w-4 h-4 shrink-0" />
            <span>{error}</span>
          </div>
          <button
            onClick={onRetry}
            className="px-3 py-1 bg-rose-900 hover:bg-rose-800 text-rose-100 rounded text-xs transition"
          >
            Retry Risk Assessment
          </button>
        </div>
      )}

      {!loading && !error && data && styles && (
        <div className="space-y-4">
          <div className="bg-slate-950/60 p-4 rounded-lg border border-slate-800 flex items-center justify-between gap-4">
            <div>
              <div className="text-xs text-slate-400 font-medium flex items-center space-x-1.5">
                <Waves className="w-3.5 h-3.5 text-blue-400" />
                <span>Hazard</span>
              </div>
              <div className="text-lg font-bold text-slate-100 mt-0.5">{formatHazardLabel(data.hazard)}</div>
              <div className="text-[11px] text-slate-500 mt-1">
                Elevated flood-related risk indicators — not a flood prediction
              </div>
            </div>
            <div className={`px-3 py-1.5 rounded-lg text-xs font-semibold border ${styles.badge}`}>
              LEVEL: {styles.label}
            </div>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
              <div className="text-[11px] text-slate-400">Risk Score</div>
              <div className={`text-2xl font-bold font-mono mt-0.5 ${styles.score}`}>{scorePct}%</div>
            </div>
            <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
              <div className="text-[11px] text-slate-400 flex items-center space-x-1">
                <Clock className="w-3 h-3" />
                <span>Forecast Window</span>
              </div>
              <div className="text-2xl font-bold font-mono text-slate-200 mt-0.5">
                {data.forecast_window_hours} hours
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wide mb-2">Key Indicators</h4>
            <div className="grid grid-cols-2 sm:grid-cols-3 gap-2">
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                <CloudRain className="w-4 h-4 text-cyan-400 mb-1" />
                <div className="text-[11px] text-slate-400">Current Rainfall</div>
                <div className="text-sm font-mono text-slate-200 mt-0.5">
                  {formatMm(data.features.current_precipitation)}
                </div>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                <CloudRain className="w-4 h-4 text-blue-400 mb-1" />
                <div className="text-[11px] text-slate-400">Forecast Rainfall</div>
                <div className="text-sm font-mono text-slate-200 mt-0.5">
                  {formatMm(data.features.forecast_precipitation)}
                </div>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                <Droplets className="w-4 h-4 text-indigo-400 mb-1" />
                <div className="text-[11px] text-slate-400">Historical Baseline</div>
                <div className="text-sm font-mono text-slate-200 mt-0.5">
                  {formatMm(data.features.historical_rainfall_baseline)}
                  <span className="text-[10px] text-slate-500"> / day</span>
                </div>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60">
                <TrendingUp className="w-4 h-4 text-amber-400 mb-1" />
                <div className="text-[11px] text-slate-400">Rainfall Anomaly</div>
                <div className="text-sm font-mono text-slate-200 mt-0.5">
                  {formatPct(data.features.rainfall_anomaly)}
                </div>
              </div>
              <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 col-span-2 sm:col-span-1">
                <Droplets className="w-4 h-4 text-teal-400 mb-1" />
                <div className="text-[11px] text-slate-400">Recent Rainfall</div>
                <div className="text-sm font-mono text-slate-200 mt-0.5">
                  {formatMm(data.features.recent_rainfall)}
                </div>
              </div>
            </div>
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wide mb-2">Why this risk?</h4>
            {data.drivers.length === 0 ? (
              <p className="text-xs text-slate-500">No feature-based drivers were available for this assessment.</p>
            ) : (
              <ul className="space-y-1.5">
                {data.drivers.map((driver, idx) => (
                  <li
                    key={`${driver.feature}-${idx}`}
                    className="text-xs text-slate-300 bg-slate-950/40 border border-slate-800/60 rounded-lg px-3 py-2"
                  >
                    {driver.message}
                  </li>
                ))}
              </ul>
            )}
          </div>

          <div>
            <h4 className="text-xs font-semibold text-slate-300 uppercase tracking-wide mb-2">Recommended Actions</h4>
            <ul className="space-y-1.5">
              {data.recommended_actions.map((action) => (
                <li
                  key={action}
                  className="text-xs text-slate-300 bg-slate-950/40 border border-slate-800/60 rounded-lg px-3 py-2"
                >
                  {action}
                </li>
              ))}
            </ul>
          </div>

          <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 flex items-start space-x-3">
            <Cpu className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div className="text-xs text-slate-400 space-y-0.5">
              <div>
                <span className="text-slate-200 font-medium">{data.model.name}</span>
                {' · '}v{data.model.version}
                {' · '}
                <span className="uppercase tracking-wide">{data.model.type.replace(/_/g, ' ')}</span>
              </div>
              <div className="flex items-start space-x-1.5 text-[11px] text-slate-500 pt-1">
                <Info className="w-3 h-3 shrink-0 mt-0.5" />
                <span>Prototype risk assessment — not an official warning.</span>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
