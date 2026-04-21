// frontend/src/components/maps/SimpleCollectionPointsMap.jsx
import React, { useState, useEffect, useCallback, useRef } from 'react';
import { getAllCollectionPoints } from '../../services/collector';
import { getUserCollectionPoints } from '../../services/user';
import { useAuth } from '../../context/AuthContext';
import { MapPin, Package, Navigation, Clock, Activity, Wifi } from 'lucide-react';

const REFRESH_INTERVAL = 5000; // 5 seconds

const SimpleCollectionPointsMap = ({ filters = {} }) => {
  const { user } = useAuth();
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const intervalRef = useRef(null);
  
  const isCollector = user?.role === 'collector';

  const loadCollectionPoints = useCallback(async (silent = false) => {
    if (!silent) setLoading(true);
    setError('');
    try {
      let response;
      if (isCollector) {
        response = await getAllCollectionPoints(filters);
      } else {
        response = await getUserCollectionPoints(filters);
      }
      setCollectionPoints(response.collection_points || []);
    } catch (err) {
      console.error('Error loading collection points:', err);
      if (!silent) setError('Failed to load collection points: ' + (err.message || 'Unknown error'));
    } finally {
      if (!silent) setLoading(false);
    }
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [filters, isCollector, user?.role]);

  useEffect(() => {
    loadCollectionPoints();
    // Auto-refresh every 5 seconds for live IoT data
    intervalRef.current = setInterval(() => loadCollectionPoints(true), REFRESH_INTERVAL);
    return () => clearInterval(intervalRef.current);
  }, [loadCollectionPoints]);

  const handleGetDirections = (point) => {
    if (point.latitude && point.longitude) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${point.latitude},${point.longitude}`;
      window.open(url, '_blank');
    }
  };

  const getWasteTypeBadgeColor = (wasteType) => {
    const colors = {
      plastic: 'bg-blue-100 text-blue-800',
      paper: 'bg-green-100 text-green-800',
      metal: 'bg-gray-100 text-gray-800',
      glass: 'bg-purple-100 text-purple-800',
      textile: 'bg-pink-100 text-pink-800',
      organic: 'bg-yellow-100 text-yellow-800'
    };
    return colors[wasteType] || 'bg-gray-100 text-gray-800';
  };

  // Calculate fill percentage from capacity fields
  const getFillInfo = (point) => {
    const maxCap = parseFloat(point.max_capacity_kg) || 100;
    const currentCap = parseFloat(point.current_capacity_kg) || 0;
    const pct = Math.min(100, Math.max(0, (currentCap / maxCap) * 100));
    
    let color, bg, label;
    if (pct >= 90) { color = '#ef4444'; bg = '#fef2f2'; label = 'CRITICAL'; }
    else if (pct >= 70) { color = '#f97316'; bg = '#fff7ed'; label = 'HIGH'; }
    else if (pct >= 40) { color = '#eab308'; bg = '#fefce8'; label = 'MODERATE'; }
    else { color = '#22c55e'; bg = '#f0fdf4'; label = 'LOW'; }
    
    return { pct, color, bg, label, currentCap, maxCap };
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
        <span className="ml-2">Loading collection points...</span>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        <p className="font-medium">Error loading collection points</p>
        <p className="text-sm mt-1">{error}</p>
        <button 
          onClick={() => loadCollectionPoints()}
          className="mt-2 px-3 py-1 bg-red-100 text-red-700 rounded text-sm hover:bg-red-200"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <MapPin className="text-emerald-600" />
            Collection Points ({collectionPoints.length})
          </h3>
          <div className="flex items-center gap-2 px-3 py-1 bg-emerald-50 text-emerald-700 rounded-full text-xs font-medium border border-emerald-200">
            <Wifi size={12} />
            LIVE
            <span className="relative flex h-2 w-2">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-emerald-500"></span>
            </span>
          </div>
        </div>
        <div className="flex flex-wrap gap-2 text-sm">
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-blue-500"></div>
            <span>Plastic</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-green-500"></div>
            <span>Paper</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-gray-500"></div>
            <span>Metal</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-purple-500"></div>
            <span>Glass</span>
          </div>
          <div className="flex items-center gap-1">
            <div className="w-3 h-3 rounded-full bg-pink-500"></div>
            <span>Textile</span>
          </div>
        </div>
      </div>

      {/* Collection Points List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-4 border-b">
          <h4 className="font-semibold text-gray-800">Available Collection Points</h4>
          <p className="text-xs text-gray-500 mt-1">Fill levels update every 5 seconds via IoT sensors</p>
        </div>
        
        <div className="divide-y divide-gray-200">
          {collectionPoints.length > 0 ? (
            collectionPoints.map(point => {
              const fill = getFillInfo(point);
              return (
                <div key={point.point_id} className="p-4 hover:bg-gray-50">
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1">
                      <div className="flex items-center gap-2">
                        <h5 className="font-semibold text-gray-800">{point.point_name}</h5>
                        {fill.pct > 0 && (
                          <span className="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium"
                                style={{ backgroundColor: fill.bg, color: fill.color }}>
                            <Activity size={10} />
                            IoT
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-gray-600">{point.colony_name}</p>
                      {point.location_description && (
                        <p className="text-xs text-gray-500 mt-1">{point.location_description}</p>
                      )}
                    </div>
                    
                    {point.latitude && point.longitude && (
                      <button
                        onClick={() => handleGetDirections(point)}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm"
                      >
                        <Navigation size={14} />
                        Directions
                      </button>
                    )}
                  </div>

                  {/* Waste Types */}
                  <div className="mb-3">
                    <p className="text-xs font-medium text-gray-700 mb-1 flex items-center gap-1">
                      <Package size={12} />
                      Accepts:
                    </p>
                    <div className="flex flex-wrap gap-1">
                      {point.waste_types_accepted && point.waste_types_accepted.map(type => (
                        <span
                          key={type}
                          className={`px-2 py-1 rounded-full text-xs font-medium ${getWasteTypeBadgeColor(type)}`}
                        >
                          {type.charAt(0).toUpperCase() + type.slice(1)}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* LIVE Fill Level Bar */}
                  <div className="mb-2">
                    <div className="flex justify-between text-xs text-gray-600 mb-1">
                      <span className="flex items-center gap-1">
                        <Activity size={10} className="text-emerald-500" />
                        Fill Level:
                      </span>
                      <span className="font-bold" style={{ color: fill.color }}>
                        {fill.pct.toFixed(1)}% — {fill.label}
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3 overflow-hidden">
                      <div
                        className="h-3 rounded-full transition-all duration-1000 ease-out"
                        style={{
                          width: `${Math.max(2, fill.pct)}%`,
                          backgroundColor: fill.color
                        }}
                      ></div>
                    </div>
                    <div className="flex justify-between text-xs text-gray-400 mt-0.5">
                      <span>{fill.currentCap.toFixed(1)} kg</span>
                      <span>{fill.maxCap.toFixed(0)} kg max</span>
                    </div>
                  </div>

                  {/* Last Collection */}
                  {point.last_collection_date && (
                    <p className="text-xs text-gray-500 flex items-center gap-1">
                      <Clock size={10} />
                      Last collection: {new Date(point.last_collection_date).toLocaleDateString()}
                    </p>
                  )}

                  {/* Location Info */}
                  {point.latitude && point.longitude && (
                    <p className="text-xs text-gray-500 mt-2">
                      📍 {parseFloat(point.latitude).toFixed(4)}, {parseFloat(point.longitude).toFixed(4)}
                    </p>
                  )}
                </div>
              );
            })
          ) : (
            <div className="p-8 text-center text-gray-500">
              <MapPin size={48} className="mx-auto mb-4 text-gray-300" />
              <p>No collection points found</p>
              <p className="text-sm mt-2">Collection points may need to be set up by administrators.</p>
            </div>
          )}
        </div>
      </div>

      {/* Google Maps Integration */}
      {collectionPoints.length > 0 && (
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h4 className="font-semibold text-gray-800 mb-3">View on Google Maps</h4>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {collectionPoints.slice(0, 4).map(point => (
              <button
                key={point.point_id}
                onClick={() => handleGetDirections(point)}
                className="flex items-center justify-between p-2 border rounded hover:bg-gray-50 text-left"
              >
                <div>
                  <p className="font-medium text-sm">{point.point_name}</p>
                  <p className="text-xs text-gray-600">{point.colony_name}</p>
                </div>
                <Navigation size={16} className="text-blue-600" />
              </button>
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default SimpleCollectionPointsMap;