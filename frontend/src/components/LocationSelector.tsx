import React, { useState } from 'react';
import { MapPin, Navigation } from 'lucide-react';

export interface LocationPreset {
  label: string;
  lat: number;
  lon: number;
}

export const PRESET_LOCATIONS: LocationPreset[] = [
  { label: 'Disaster Sector Alpha (Kanchipuram, TN)', lat: 12.8342, lon: 79.7036 },
  { label: 'New Delhi, NCR', lat: 28.6139, lon: 77.2090 },
  { label: 'Mumbai, Maharashtra', lat: 19.0760, lon: 72.8777 },
  { label: 'Kolkata, West Bengal', lat: 22.5726, lon: 88.3639 },
  { label: 'Chennai, Tamil Nadu', lat: 13.0827, lon: 80.2707 },
  { label: 'Shimla, Himachal Pradesh', lat: 31.1048, lon: 77.1734 },
];

interface LocationSelectorProps {
  currentLat: number;
  currentLon: number;
  onLocationSelect: (lat: number, lon: number, label: string) => void;
}

export const LocationSelector: React.FC<LocationSelectorProps> = ({
  currentLat,
  currentLon,
  onLocationSelect,
}) => {
  const [selectedPreset, setSelectedPreset] = useState<string>(PRESET_LOCATIONS[0].label);
  const [inputLat, setInputLat] = useState<string>(currentLat.toString());
  const [inputLon, setInputLon] = useState<string>(currentLon.toString());
  const [isCustomMode, setIsCustomMode] = useState<boolean>(false);

  const handleDropdownChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const val = e.target.value;
    setSelectedPreset(val);
    if (val === 'CUSTOM') {
      setIsCustomMode(true);
    } else {
      setIsCustomMode(false);
      const found = PRESET_LOCATIONS.find((loc) => loc.label === val);
      if (found) {
        setInputLat(found.lat.toString());
        setInputLon(found.lon.toString());
        onLocationSelect(found.lat, found.lon, found.label);
      }
    }
  };

  const handleCustomSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const parsedLat = parseFloat(inputLat);
    const parsedLon = parseFloat(inputLon);

    if (isNaN(parsedLat) || parsedLat < -90 || parsedLat > 90) {
      alert('Please enter a valid latitude between -90 and 90');
      return;
    }
    if (isNaN(parsedLon) || parsedLon < -180 || parsedLon > 180) {
      alert('Please enter a valid longitude between -180 and 180');
      return;
    }

    const label = `Custom Location (${parsedLat.toFixed(4)}, ${parsedLon.toFixed(4)})`;
    onLocationSelect(parsedLat, parsedLon, label);
  };

  return (
    <div className="bg-slate-900/80 backdrop-blur border border-slate-800 rounded-xl p-4 shadow-sm">
      <div className="flex flex-col lg:flex-row items-start lg:items-center justify-between gap-4">
        {/* Title */}
        <div className="flex items-center space-x-2.5">
          <div className="p-2 bg-slate-800 rounded-lg text-cyan-400">
            <MapPin className="w-5 h-5" />
          </div>
          <div>
            <h2 className="text-sm font-semibold text-slate-200">Location & Coordinates Engine</h2>
            <p className="text-xs text-slate-400">Select preset or enter custom latitude & longitude</p>
          </div>
        </div>

        {/* Selector & Inputs */}
        <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-3 w-full lg:w-auto">
          {/* Preset Dropdown */}
          <div className="relative">
            <select
              value={isCustomMode ? 'CUSTOM' : selectedPreset}
              onChange={handleDropdownChange}
              className="w-full sm:w-64 bg-slate-950 border border-slate-700/80 rounded-lg px-3 py-2 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 transition cursor-pointer"
            >
              {PRESET_LOCATIONS.map((loc) => (
                <option key={loc.label} value={loc.label}>
                  {loc.label}
                </option>
              ))}
              <option value="CUSTOM">Custom Geo-Coordinates...</option>
            </select>
          </div>

          {/* Coordinate Form */}
          <form onSubmit={handleCustomSubmit} className="flex items-center space-x-2">
            <div className="flex items-center space-x-1.5 bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs">
              <span className="text-slate-500 font-mono">LAT:</span>
              <input
                type="number"
                step="any"
                min="-90"
                max="90"
                value={inputLat}
                onChange={(e) => setInputLat(e.target.value)}
                className="w-20 bg-transparent text-slate-100 font-mono focus:outline-none"
                placeholder="Latitude"
              />
            </div>

            <div className="flex items-center space-x-1.5 bg-slate-950 border border-slate-700/80 rounded-lg px-2.5 py-1.5 text-xs">
              <span className="text-slate-500 font-mono">LON:</span>
              <input
                type="number"
                step="any"
                min="-180"
                max="180"
                value={inputLon}
                onChange={(e) => setInputLon(e.target.value)}
                className="w-20 bg-transparent text-slate-100 font-mono focus:outline-none"
                placeholder="Longitude"
              />
            </div>

            <button
              type="submit"
              className="px-3 py-2 bg-cyan-600 hover:bg-cyan-500 text-slate-950 font-semibold rounded-lg text-xs transition flex items-center space-x-1 shrink-0 shadow-sm shadow-cyan-500/20"
            >
              <Navigation className="w-3.5 h-3.5" />
              <span>Fetch</span>
            </button>
          </form>
        </div>
      </div>

      {/* Coordinate bar info */}
      <div className="mt-3 pt-2 border-t border-slate-800/60 flex flex-wrap items-center justify-between text-[11px] text-slate-400 gap-2">
        <div className="flex items-center space-x-1.5">
          <span className="text-slate-500">Active Coordinates:</span>
          <span className="font-mono text-cyan-400 font-medium">
            {currentLat.toFixed(4)}° N, {currentLon.toFixed(4)}° E
          </span>
        </div>
        <div className="flex items-center space-x-1 text-slate-500">
          <span>Targeting Backend:</span>
          <code className="text-slate-400 font-mono">GET /api/v1/weather/current?lat={currentLat}&lon={currentLon}</code>
        </div>
      </div>
    </div>
  );
};
