// frontend/src/pages/IoTMonitor.jsx
// Live IoT bin fill-level monitoring page
// Polls backend every 5 seconds and shows a real-time fill bar

import React, { useState, useEffect, useRef } from 'react';
import { Activity, Wifi, WifiOff, Trash2, TrendingUp, Clock, Gauge } from 'lucide-react';

const POLL_INTERVAL = 5000; // 5 seconds
const POINT_NAME = 'hii';  // Collection point name to monitor

// Color based on fill level
const getFillColor = (pct) => {
  if (pct >= 90) return { bar: '#ef4444', bg: '#fef2f2', text: '#991b1b', label: 'CRITICAL' };
  if (pct >= 70) return { bar: '#f97316', bg: '#fff7ed', text: '#9a3412', label: 'HIGH' };
  if (pct >= 40) return { bar: '#eab308', bg: '#fefce8', text: '#854d0e', label: 'MODERATE' };
  return { bar: '#22c55e', bg: '#f0fdf4', text: '#166534', label: 'LOW' };
};

const IoTMonitor = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [connected, setConnected] = useState(false);
  const [lastPoll, setLastPoll] = useState(null);
  const [pollCount, setPollCount] = useState(0);
  const intervalRef = useRef(null);

  const API_BASE = process.env.REACT_APP_API_URL || 'https://smartwaste360-backend.onrender.com/api';

  const fetchLiveData = async () => {
    try {
      const url = `${API_BASE}/iot/live/${encodeURIComponent(POINT_NAME)}`;
      const res = await fetch(url);
      
      if (!res.ok) {
        throw new Error(`Server responded with ${res.status}`);
      }
      
      const json = await res.json();
      setData(json);
      setConnected(true);
      setError(null);
      setLastPoll(new Date());
      setPollCount(prev => prev + 1);
    } catch (err) {
      console.error('[IoT Poll]', err.message);
      setError(err.message);
      setConnected(false);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveData();
    intervalRef.current = setInterval(fetchLiveData, POLL_INTERVAL);
    return () => clearInterval(intervalRef.current);
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const fillPct = data?.fill_percentage ?? 0;
  const colors = getFillColor(fillPct);

  if (loading && !data) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-4 border-emerald-500 border-t-transparent mx-auto mb-4"></div>
          <p className="text-gray-600">Connecting to sensor...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 md:p-6">
      <div className="max-w-4xl mx-auto space-y-6">

        {/* Header */}
        <div className="bg-white rounded-2xl shadow-sm border p-6">
          <div className="flex items-center justify-between flex-wrap gap-4">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center">
                <Activity className="text-emerald-600" size={24} />
              </div>
              <div>
                <h1 className="text-2xl font-bold text-gray-800">IoT Bin Monitor</h1>
                <p className="text-sm text-gray-500">Real-time ultrasonic sensor data</p>
              </div>
            </div>
            
            {/* Connection status */}
            <div className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium ${
              connected 
                ? 'bg-emerald-50 text-emerald-700 border border-emerald-200' 
                : 'bg-red-50 text-red-700 border border-red-200'
            }`}>
              {connected ? <Wifi size={16} /> : <WifiOff size={16} />}
              {connected ? 'LIVE' : 'DISCONNECTED'}
              {connected && (
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Error banner */}
        {error && (
          <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3">
            <WifiOff className="text-red-500 flex-shrink-0" size={20} />
            <div>
              <p className="font-medium text-red-800">Connection Error</p>
              <p className="text-sm text-red-600">{error}</p>
              <p className="text-xs text-red-500 mt-1">Retrying every {POLL_INTERVAL/1000}s...</p>
            </div>
          </div>
        )}

        {/* Main Fill Level Card */}
        <div className="bg-white rounded-2xl shadow-sm border overflow-hidden">
          <div className="p-6">
            <div className="flex items-center justify-between mb-2">
              <div>
                <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
                  <Trash2 size={20} />
                  Collection Point: <span className="text-emerald-600">"{data?.point_name || POINT_NAME}"</span>
                </h2>
                <p className="text-sm text-gray-500 mt-1">
                  {data?.colony_name || 'Loading...'} • Device: {data?.device_id || 'Waiting for sensor...'}
                </p>
              </div>
              <span className={`px-3 py-1 rounded-full text-xs font-bold`}
                    style={{ backgroundColor: colors.bg, color: colors.text }}>
                {colors.label}
              </span>
            </div>
          </div>

          {/* Giant fill bar */}
          <div className="px-6 pb-6">
            <div className="flex items-end justify-between mb-3">
              <span className="text-6xl font-black tabular-nums" style={{ color: colors.bar }}>
                {fillPct.toFixed(1)}%
              </span>
              <span className="text-gray-400 text-sm mb-2">
                {data?.estimated_weight_kg?.toFixed(2) || '0.00'} / {data?.max_capacity_kg?.toFixed(0) || '100'} kg
              </span>
            </div>
            
            {/* Fill bar */}
            <div className="w-full bg-gray-100 rounded-full h-8 overflow-hidden relative">
              <div
                className="h-full rounded-full transition-all duration-1000 ease-out relative"
                style={{ 
                  width: `${Math.max(2, fillPct)}%`,
                  backgroundColor: colors.bar 
                }}
              >
                {/* Animated shimmer */}
                <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-pulse"></div>
              </div>
              {/* Bar labels */}
              <div className="absolute inset-0 flex items-center justify-between px-3">
                <span className="text-xs font-bold text-white drop-shadow-sm" 
                      style={{ visibility: fillPct > 10 ? 'visible' : 'hidden' }}>
                  {fillPct.toFixed(0)}%
                </span>
              </div>
            </div>

            {/* Scale markers */}
            <div className="flex justify-between mt-1 px-1">
              {[0, 25, 50, 75, 100].map(mark => (
                <span key={mark} className="text-xs text-gray-400">{mark}%</span>
              ))}
            </div>
          </div>
        </div>

        {/* Stats cards */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <StatCard
            icon={<Gauge size={20} />}
            label="Distance"
            value={data?.distance_cm > 0 ? `${data.distance_cm.toFixed(1)} cm` : '—'}
            color="blue"
          />
          <StatCard
            icon={<TrendingUp size={20} />}
            label="Weight"
            value={`${(data?.estimated_weight_kg || 0).toFixed(2)} kg`}
            color="emerald"
          />
          <StatCard
            icon={<Activity size={20} />}
            label="Data Source"
            value={data?.source === 'sensor' ? 'Live Sensor' : 'Database'}
            color={data?.source === 'sensor' ? 'emerald' : 'gray'}
          />
          <StatCard
            icon={<Clock size={20} />}
            label="Polls"
            value={`${pollCount}`}
            color="purple"
            subtitle={lastPoll ? `Last: ${lastPoll.toLocaleTimeString()}` : ''}
          />
        </div>

        {/* Visual bin representation */}
        <div className="bg-white rounded-2xl shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Bin Visualization</h3>
          <div className="flex items-end justify-center gap-8">
            {/* Bin visual */}
            <div className="relative">
              <div className="w-40 h-64 border-4 border-gray-300 rounded-b-2xl relative overflow-hidden bg-gray-50"
                   style={{ borderTop: '8px solid #6b7280' }}>
                {/* Sensor at top */}
                <div className="absolute top-0 left-1/2 -translate-x-1/2 z-10 bg-blue-500 text-white text-xs px-2 py-0.5 rounded-b font-mono">
                  SENSOR
                </div>
                
                {/* Distance line */}
                {data?.distance_cm > 0 && (
                  <div className="absolute top-4 left-1/2 -translate-x-1/2 flex flex-col items-center"
                       style={{ height: `${Math.min(85, (1 - fillPct/100) * 85)}%` }}>
                    <div className="w-px h-full border-l-2 border-dashed border-blue-400"></div>
                    <span className="text-xs text-blue-600 font-mono whitespace-nowrap mt-1">
                      {data.distance_cm.toFixed(1)} cm
                    </span>
                  </div>
                )}
                
                {/* Fill level */}
                <div 
                  className="absolute bottom-0 left-0 right-0 transition-all duration-1000 ease-out"
                  style={{ 
                    height: `${fillPct}%`,
                    backgroundColor: colors.bar,
                    opacity: 0.3
                  }}
                ></div>
                <div 
                  className="absolute bottom-0 left-0 right-0 transition-all duration-1000 ease-out"
                  style={{ 
                    height: `${fillPct}%`,
                    background: `repeating-linear-gradient(45deg, transparent, transparent 5px, ${colors.bar}33 5px, ${colors.bar}33 10px)`,
                    borderTop: `3px solid ${colors.bar}`
                  }}
                ></div>
              </div>
              <div className="text-center mt-2 font-semibold text-gray-700">
                {fillPct.toFixed(1)}% Full
              </div>
            </div>

            {/* Legend */}
            <div className="space-y-3 text-sm">
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 bg-blue-500 rounded"></div>
                <span>Ultrasonic Sensor (HC-SR04)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-1 border-t-2 border-dashed border-blue-400" style={{width: '16px'}}></div>
                <span>Distance ({data?.distance_cm?.toFixed(1) || '—'} cm)</span>
              </div>
              <div className="flex items-center gap-2">
                <div className="w-4 h-4 rounded" style={{ backgroundColor: colors.bar, opacity: 0.4 }}></div>
                <span>Waste Level ({fillPct.toFixed(1)}%)</span>
              </div>
              <div className="mt-4 p-3 bg-gray-50 rounded-lg text-xs text-gray-600">
                <p><strong>Bin height:</strong> 30 cm</p>
                <p><strong>Updates:</strong> Every 5 seconds</p>
                <p><strong>Sensor:</strong> HC-SR04 via ESP32</p>
              </div>
            </div>
          </div>
        </div>

        {/* Reading history */}
        {data?.history && data.history.length > 0 && (
          <div className="bg-white rounded-2xl shadow-sm border p-6">
            <h3 className="text-lg font-semibold text-gray-800 mb-4">Recent Readings</h3>
            <div className="overflow-x-auto">
              <div className="flex items-end gap-1 h-32 min-w-fit">
                {data.history.map((h, i) => (
                  <div key={i} className="flex flex-col items-center gap-1" style={{ minWidth: '36px' }}>
                    <span className="text-xs text-gray-500">{h.fill.toFixed(0)}%</span>
                    <div
                      className="w-6 rounded-t transition-all duration-300"
                      style={{
                        height: `${Math.max(4, h.fill)}%`,
                        backgroundColor: getFillColor(h.fill).bar
                      }}
                    ></div>
                    <span className="text-xs text-gray-400 -rotate-45 origin-top-left whitespace-nowrap">
                      {h.time}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Last updated footer */}
        <div className="text-center text-xs text-gray-400 pb-8">
          Polling every {POLL_INTERVAL/1000}s • {data?.last_update 
            ? `Last sensor data: ${new Date(data.last_update).toLocaleString()}`
            : 'Waiting for first sensor reading...'
          }
        </div>
      </div>
    </div>
  );
};

// Stat card component
const StatCard = ({ icon, label, value, color, subtitle }) => {
  const colorMap = {
    blue: 'bg-blue-50 text-blue-600',
    emerald: 'bg-emerald-50 text-emerald-600',
    purple: 'bg-purple-50 text-purple-600',
    gray: 'bg-gray-50 text-gray-600',
  };
  return (
    <div className="bg-white rounded-xl shadow-sm border p-4">
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center mb-2 ${colorMap[color]}`}>
        {icon}
      </div>
      <p className="text-xs text-gray-500">{label}</p>
      <p className="text-lg font-bold text-gray-800">{value}</p>
      {subtitle && <p className="text-xs text-gray-400 mt-0.5">{subtitle}</p>}
    </div>
  );
};

export default IoTMonitor;
