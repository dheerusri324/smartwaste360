// frontend/src/components/maps/SimpleCollectionPointsMap.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { getAllCollectionPoints } from '../../services/collector';
import { MapPin, Package, Navigation, Clock } from 'lucide-react';

const SimpleCollectionPointsMap = ({ filters = {} }) => {
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadCollectionPoints = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      console.log('Loading collection points with filters:', filters);
      const response = await getAllCollectionPoints(filters);
      console.log('Collection points response:', response);
      setCollectionPoints(response.collection_points || []);
    } catch (err) {
      console.error('Error loading collection points:', err);
      setError('Failed to load collection points: ' + (err.message || 'Unknown error'));
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    loadCollectionPoints();
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
          onClick={loadCollectionPoints}
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
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <MapPin className="text-emerald-600" />
          Collection Points ({collectionPoints.length})
        </h3>
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
        </div>
        
        <div className="divide-y divide-gray-200">
          {collectionPoints.length > 0 ? (
            collectionPoints.map(point => (
              <div key={point.point_id} className="p-4 hover:bg-gray-50">
                <div className="flex justify-between items-start mb-3">
                  <div className="flex-1">
                    <h5 className="font-semibold text-gray-800">{point.point_name}</h5>
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

                {/* Capacity */}
                <div className="mb-2">
                  <div className="flex justify-between text-xs text-gray-600 mb-1">
                    <span>Capacity:</span>
                    <span>{parseFloat(point.current_capacity_kg || 0).toFixed(1)} / {parseFloat(point.max_capacity_kg || 0).toFixed(1)} kg</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-emerald-600 h-2 rounded-full"
                      style={{
                        width: `${Math.min(100, (point.current_capacity_kg / point.max_capacity_kg) * 100)}%`
                      }}
                    ></div>
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
            ))
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