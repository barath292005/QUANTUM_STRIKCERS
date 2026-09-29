import React from 'react';
import { CloudLightning, Activity, Server, RefreshCw, AlertTriangle } from 'lucide-react';

interface HeaderProps {
  healthStatus: { status: string; service: string } | null;
  loading: boolean;
  error: string | null;
  onRetry: () => void;
}

export const Header: React.FC<HeaderProps> = ({ healthStatus, loading, error, onRetry }) => {
  return (
    <header className="bg-slate-900 border-b border-slate-800 sticky top-0 z-50 backdrop-blur-md bg-opacity-90">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3.5 flex flex-col sm:flex-row items-center justify-between gap-4">
        {/* Brand & System Title */}
        <div className="flex items-center space-x-3">
          <div className="p-2.5 bg-gradient-to-tr from-cyan-600 to-blue-600 rounded-xl shadow-lg shadow-cyan-500/20 text-white">
            <CloudLightning className="w-6 h-6 animate-pulse" />
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <h1 className="text-xl font-bold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent">
                WeatherGPT
              </h1>
              <span className="text-[10px] uppercase tracking-wider font-semibold px-2 py-0.5 rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                v1.0 Architecture Foundation
              </span>
            </div>
            <p className="text-xs text-slate-400">
              AI-Powered Impact-Based Weather Intelligence Platform
            </p>
          </div>
        </div>

        {/* Backend Operational Status Indicator */}
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2 px-3 py-1.5 rounded-lg bg-slate-800/80 border border-slate-700/60 text-xs">
            <Server className="w-4 h-4 text-slate-400" />
            <span className="text-slate-400 font-medium">Core API:</span>
            {loading ? (
              <span className="flex items-center space-x-1.5 text-amber-400">
                <RefreshCw className="w-3.5 h-3.5 animate-spin" />
                <span>Checking...</span>
              </span>
            ) : error ? (
              <span className="flex items-center space-x-1.5 text-rose-400">
                <AlertTriangle className="w-3.5 h-3.5" />
                <span>Offline</span>
              </span>
            ) : healthStatus ? (
              <span className="flex items-center space-x-1.5 text-emerald-400 font-medium">
                <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
                <span>{healthStatus.service} ({healthStatus.status.toUpperCase()})</span>
              </span>
            ) : (
              <span className="text-slate-500">Unknown</span>
            )}
            {error && (
              <button
                onClick={onRetry}
                className="ml-2 text-xs text-cyan-400 hover:text-cyan-300 underline font-medium"
              >
                Retry
              </button>
            )}
          </div>

          <div className="hidden md:flex items-center space-x-1 text-xs text-slate-400 bg-slate-800/50 px-3 py-1.5 rounded-lg border border-slate-700/40">
            <Activity className="w-3.5 h-3.5 text-cyan-400" />
            <span>SIH Disaster Tech Core</span>
          </div>
        </div>
      </div>
    </header>
  );
};
