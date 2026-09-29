import React from 'react';
import { Bell, AlertOctagon, Info, Megaphone } from 'lucide-react';

export const AlertPanel: React.FC = () => {
  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-5 shadow-sm space-y-4">
      <div className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div className="flex items-center space-x-2">
          <Bell className="w-5 h-5 text-amber-400" />
          <h3 className="text-base font-semibold text-slate-100">Disaster Advisory Feed</h3>
        </div>
        <span className="text-xs px-2.5 py-1 rounded-md bg-slate-800 text-slate-400 font-mono border border-slate-700/50">
          Alert Pipeline Placeholder
        </span>
      </div>

      <div className="space-y-2.5">
        {/* Advisory Item 1 */}
        <div className="p-3 bg-amber-950/20 border border-amber-800/40 rounded-lg flex items-start space-x-3">
          <AlertOctagon className="w-4 h-4 text-amber-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-0.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-amber-300">Heavy Rainfall Advisory [ORANGE]</span>
              <span className="text-[10px] text-amber-500/80 font-mono">STANDBY</span>
            </div>
            <p className="text-slate-400">IMD advisory ingestion pipeline ready in backend/app/services/alerts</p>
          </div>
        </div>

        {/* Advisory Item 2 */}
        <div className="p-3 bg-slate-950/40 border border-slate-800 rounded-lg flex items-start space-x-3">
          <Info className="w-4 h-4 text-cyan-400 shrink-0 mt-0.5" />
          <div className="text-xs space-y-0.5">
            <div className="flex items-center justify-between">
              <span className="font-semibold text-slate-300">System Initialization Notice</span>
              <span className="text-[10px] text-slate-500 font-mono">SYSTEM</span>
            </div>
            <p className="text-slate-400">WeatherGPT architecture initialized for SIH multi-channel alert dispatch.</p>
          </div>
        </div>
      </div>

      <div className="bg-slate-950/40 p-3 rounded-lg border border-slate-800/60 flex items-center space-x-3">
        <Megaphone className="w-4 h-4 text-amber-400 shrink-0" />
        <div className="text-xs text-slate-400">
          <span className="text-slate-200 font-medium">Broadcast & Alert Service:</span> Configured at <code className="text-amber-400 font-mono">backend/app/services/alerts/</code>.
        </div>
      </div>
    </div>
  );
};
