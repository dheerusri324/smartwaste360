// frontend/src/components/maps/CollectionPointsMap.jsx
import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, useMap } from 'react-leaflet';
import { getAllCollectionPoints } from '../../services/collector';
import { MapPin, Package, Navigation, Clock } from 'lucide-react';
import L from 'leaflet';
import 'leaflet/dist/leaflet.css';

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom icons for different waste types
const createCustomIcon = (wasteTypes) => {
  const color = getWasteTypeColor(wasteTypes);
  return L.divIcon({
    html: `<div style="background-color: ${color}; width: 20px; height: 20px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    className: 'custom-marker',
    iconSize: [20, 20],
    iconAnchor: [10, 10]
  });
};

const getWasteTypeColor = (wasteTypes) => {
  if (!wasteTypes || wasteTypes.length === 0) return '#6B7280';
  
  // Priority colors based on waste type
  if (wasteTypes.includes('plastic')) return '#3B82F6'; // Blue
  if (wasteTypes.includes('paper')) return '#10B981'; // Green
  if (wasteTypes.includes('metal')) return '#6B7280'; // Gray
  if (wasteTypes.includes('glass')) return '#8B5CF6'; // Purple
  if (wasteTypes.includes('textile')) return '#EC4899'; // Pink
  if (wasteTypes.includes('organic')) return '#F59E0B'; // Yellow
  
  return '#6B7280'; // Default gray
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

const MapUpdater = ({ center }) => {
  const map = useMap();
  useEffect(() => {
    if (center) {
      map.setView(center, 13);
    }
  }, [center, map]);
  return null;
};

const CollectionPointsMap = ({ filters = {}, onPointSelect }) => {
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [mapCenter, setMapCenter] = useState([28.6139, 77.2090]); // Default to Delhi

  useEffect(() => {
    loadCollectionPoints();
  }, [filters]);

  useEffect(() => {
    // Try to get user's location
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setMapCenter([position.coords.latitude, position.coords.longitude]);
        },
        (error) => {
          console.log('Geolocation error:', error);
          // Keep default location
        }
      );
    }
  }, []);

  const loadCollectionPoints = async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getAllCollectionPoints(filters);
      setCollectionPoints(response.collection_points || []);
    } catch (err) {
      setError('Failed to load collection points');
      console.error('Error loading collection points:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleGetDirections = (point) => {
    if (point.latitude && point.longitude) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${point.latitude},${point.longitude}`;
      window.open(url, '_blank');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-96">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
        {error}
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Map Legend */}
      <div className="bg-white p-4 rounded-lg shadow-sm border">
        <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center gap-2">
          <MapPin className="text-emerald-600" />
          Collection Points Map
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
        <p className="text-sm text-gray-600 mt-2">
          Found {collectionPoints.length} collection points
        </p>
      </div>

      {/* Map */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <MapContainer
          center={mapCenter}
          zoom={13}
          style={{ height: '500px', width: '100%' }}
        >
          <MapUpdater center={mapCenter} />
          <TileLayer
            attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          
          {collectionPoints.map(point => (
            point.latitude && point.longitude && (
              <Marker
                key={point.point_id}
                position={[parseFloat(point.latitude), parseFloat(point.longitude)]}
                icon={createCustomIcon(point.waste_types_accepted)}
              >
                <Popup maxWidth={300}>
                  <div className="p-2">
                    <h4 className="font-semibold text-gray-800 mb-1">
                      {point.point_name}
                    </h4>
                    <p className="text-sm text-gray-600 mb-2">
                      {point.colony_name}
                    </p>
                    
                    {point.location_description && (
                      <p className="text-xs text-gray-500 mb-2">
                        {point.location_description}
                      </p>
                    )}

                    {/* Waste Types */}
                    <div className="mb-2">
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
                      <p className="text-xs text-gray-600">
                        Capacity: {parseFloat(point.current_capacity_kg || 0).toFixed(1)} / {parseFloat(point.max_capacity_kg || 0).toFixed(1)} kg
                      </p>
                      <div className="w-full bg-gray-200 rounded-full h-1.5 mt-1">
                        <div
                          className="bg-emerald-600 h-1.5 rounded-full"
                          style={{
                            width: `${Math.min(100, (point.current_capacity_kg / point.max_capacity_kg) * 100)}%`
                          }}
                        ></div>
                      </div>
                    </div>

                    {/* Last Collection */}
                    {point.last_collection_date && (
                      <p className="text-xs text-gray-500 mb-2 flex items-center gap-1">
                        <Clock size={10} />
                        Last collection: {new Date(point.last_collection_date).toLocaleDateString()}
                      </p>
                    )}

                    {/* Actions */}
                    <div className="flex gap-2 mt-2">
                      <button
                        onClick={() => handleGetDirections(point)}
                        className="flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200 transition-colors"
                      >
                        <Navigation size={10} />
                        Directions
                      </button>
                      {onPointSelect && (
                        <button
                          onClick={() => onPointSelect(point)}
                          className="flex items-center gap-1 px-2 py-1 bg-emerald-100 text-emerald-700 rounded text-xs hover:bg-emerald-200 transition-colors"
                        >
                          Select
                        </button>
                      )}
                    </div>
                  </div>
                </Popup>
              </Marker>
            )
          ))}
        </MapContainer>
      </div>

      {/* Collection Points List */}
      <div className="bg-white rounded-lg shadow-sm border p-4">
        <h4 className="font-semibold text-gray-800 mb-3">Collection Points List</h4>
        <div className="space-y-2 max-h-60 overflow-y-auto">
          {collectionPoints.map(point => (
            <div key={point.point_id} className="flex justify-between items-center p-2 border rounded hover:bg-gray-50">
              <div>
                <p className="font-medium text-sm">{point.point_name}</p>
                <p className="text-xs text-gray-600">{point.colony_name}</p>
              </div>
              <div className="flex gap-1">
                <button
                  onClick={() => handleGetDirections(point)}
                  className="px-2 py-1 bg-blue-100 text-blue-700 rounded text-xs hover:bg-blue-200 transition-colors"
                >
                  Directions
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default CollectionPointsMap;