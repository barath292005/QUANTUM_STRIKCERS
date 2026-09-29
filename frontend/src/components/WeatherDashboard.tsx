import React from 'react';
import {
  Sun,
  CloudRain,
  CloudLightning,
  Cloud,
  Thermometer,
  Wind,
  Droplets,
  Gauge,
  CloudDrizzle,
  Clock,
  Database,
  RefreshCw,
  AlertTriangle,
} from 'lucide-react';

export interface CurrentWeatherData {
  latitude: number;
  longitude: number;
  temperature: number;
  feels_like: number;
  humidity: number;
  pressure: number;
  wind_speed: number;
  wind_direction: number;
  precipitation: number;
  condition: string;
  visibility?: number | null;
  observation_time: string;
  data_source: string;
}

export interface LocationData {
  latitude: number;
  longitude: number;
  city?: string | null;
  country?: string | null;
  timezone?: string | null;
}

export interface WeatherResponseData {
  location: LocationData;
  current: CurrentWeatherData;
}

interface WeatherDashboardProps {
  weather: WeatherResponseData | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export const WeatherDashboard: React.FC<WeatherDashboardProps> = ({
  weather,
  loading,
  error,
  onRetry,
}) => {
  const getConditionIcon = (condition: string) => {
    const cond = condition.toLowerCase();
    if (cond.includes('thunder') || cond.includes('storm')) {
      return <CloudLightning className="w-8 h-8 text-amber-400 animate-pulse" />;
    }
    if (cond.includes('rain') || cond.includes('shower')) {
      return <CloudRain className="w-8 h-8 text-cyan-400" />;
    }
    if (cond.includes('drizzle')) {
      return <CloudDrizzle className="w-8 h-8 text-teal-400" />;
    }
    if (cond.includes('cloud') || cond.includes('overcast')) {
      return <Cloud className="w-8 h-8 text-slate-300" />;
    }
    return <Sun className="w-8 h-8 text-amber-400" />;
  };

  const formatObservationTime = (isoTime: string) => {
    if (!isoTime) return 'N/A';
    try {
      const date = new Date(isoTime);
      return isNaN(date.getTime()) ? isoTime : date.toLocaleString();
    } catch {
      return isoTime;
    }
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      {/* Header Bar */}
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Sun className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-slate-100">Real-Time Weather Telemetry</h3>
        </div>
        {weather && (
          <span className="text-xs px-2.5 py-1 rounded-md bg-emerald-950/60 text-emerald-400 font-mono border border-emerald-800/50 flex items-center space-x-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
            <span>LIVE DATA</span>
          </span>
        )}
      </div>

      {/* Loading State */}
      {loading && (
        <div className="py-12 flex flex-col items-center justify-center space-y-3 bg-slate-950/50 rounded-lg border border-slate-800/80">
          <RefreshCw className="w-8 h-8 text-cyan-400 animate-spin" />
          <div className="text-sm font-medium text-slate-200">Loading weather data...</div>
          <p className="text-xs text-slate-500">Querying real-time weather service backend</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="p-5 bg-rose-950/40 border border-rose-800/60 rounded-lg space-y-3">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-rose-400 shrink-0 mt-0.5" />
            <div className="space-y-1">
              <h4 className="text-sm font-semibold text-rose-200">Unable to retrieve weather data</h4>
              <p className="text-xs text-rose-300/80">{error}</p>
            </div>
          </div>
          <button
            onClick={onRetry}
            className="px-3.5 py-1.5 bg-rose-900/80 hover:bg-rose-800 text-rose-100 rounded-md text-xs font-semibold border border-rose-700 transition flex items-center space-x-1.5"
          >
            <RefreshCw className="w-3.5 h-3.5" />
            <span>Please try again</span>
          </button>
        </div>
      )}

      {/* Data Available View */}
      {!loading && !error && weather && (
        <div className="space-y-4">
          {/* Top Main Condition Banner */}
          <div className="bg-gradient-to-r from-slate-950 via-slate-900 to-slate-950 p-4 rounded-xl border border-slate-800 flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center space-x-4">
              <div className="p-3 bg-slate-900 rounded-xl border border-slate-800 shadow-inner">
                {getConditionIcon(weather.current.condition)}
              </div>
              <div>
                <div className="text-2xl font-extrabold text-slate-100">
                  {weather.current.condition}
                </div>
                <div className="text-xs text-slate-400 mt-0.5">
                  Location: <span className="text-cyan-400 font-mono font-medium">{weather.location.latitude}° N, {weather.location.longitude}° E</span>
                  {weather.location.timezone && <span className="ml-2 text-slate-500">({weather.location.timezone})</span>}
                </div>
              </div>
            </div>

            <div className="text-right sm:border-l sm:border-slate-800 sm:pl-6">
              <div className="text-3xl font-extrabold text-slate-100 font-mono">
                {weather.current.temperature.toFixed(1)} <span className="text-lg text-cyan-400">°C</span>
              </div>
              <div className="text-xs text-slate-400">
                Feels like <strong className="text-slate-200 font-mono">{weather.current.feels_like.toFixed(1)} °C</strong>
              </div>
            </div>
          </div>

          {/* Metrics Grid */}
          <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-3">
            {/* Temperature */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Temp / Feels</span>
                <Thermometer className="w-4 h-4 text-amber-400" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.temperature.toFixed(1)}°C
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">
                Feels {weather.current.feels_like.toFixed(1)}°C
              </div>
            </div>

            {/* Humidity */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Humidity</span>
                <Droplets className="w-4 h-4 text-cyan-400" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.humidity.toFixed(0)}%
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Relative Moisture</div>
            </div>

            {/* Wind Speed */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Wind Speed</span>
                <Wind className="w-4 h-4 text-teal-400" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.wind_speed.toFixed(1)} <span className="text-xs font-normal">km/h</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Dir: {weather.current.wind_direction.toFixed(0)}°</div>
            </div>

            {/* Barometric Pressure */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Pressure</span>
                <Gauge className="w-4 h-4 text-indigo-400" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.pressure.toFixed(0)} <span className="text-xs font-normal">hPa</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Surface Barometric</div>
            </div>

            {/* Rainfall / Precipitation */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Rainfall</span>
                <CloudRain className="w-4 h-4 text-blue-400" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.precipitation.toFixed(1)} <span className="text-xs font-normal">mm</span>
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Current Rate</div>
            </div>

            {/* Visibility */}
            <div className="bg-slate-950/60 p-3 rounded-lg border border-slate-800/80">
              <div className="flex items-center justify-between text-slate-400 text-xs">
                <span>Visibility</span>
                <Sun className="w-4 h-4 text-amber-300" />
              </div>
              <div className="mt-2 text-base font-bold text-slate-100 font-mono">
                {weather.current.visibility != null ? `${weather.current.visibility.toFixed(1)} km` : 'N/A'}
              </div>
              <div className="text-[10px] text-slate-500 mt-0.5">Line of Sight</div>
            </div>
          </div>

          {/* Footer Metadata */}
          <div className="pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-xs text-slate-400 gap-2">
            <div className="flex items-center space-x-1.5">
              <Clock className="w-3.5 h-3.5 text-slate-500" />
              <span>Observation Time:</span>
              <strong className="text-slate-300 font-mono">{formatObservationTime(weather.current.observation_time)}</strong>
            </div>

            <div className="flex items-center space-x-1.5">
              <Database className="w-3.5 h-3.5 text-cyan-400" />
              <span>Data Source:</span>
              <span className="px-2 py-0.5 bg-slate-800 text-cyan-300 rounded font-mono text-[11px] border border-slate-700">
                {weather.current.data_source}
              </span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
