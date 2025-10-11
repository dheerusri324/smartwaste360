// frontend/src/components/collector/CollectionPointsModal.jsx
import React, { useState, useEffect, useCallback } from 'react';
import { getCollectionPoints } from '../../services/collector';
import { MapPin, Package, X, Navigation } from 'lucide-react';

const CollectionPointsModal = ({ colony, isOpen, onClose }) => {
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const loadCollectionPoints = useCallback(async () => {
    setLoading(true);
    setError('');
    try {
      const response = await getCollectionPoints(colony.colony_id);
      setCollectionPoints(response.collection_points || []);
    } catch (err) {
      setError('Failed to load collection points');
    } finally {
      setLoading(false);
    }
  }, [colony]);

  useEffect(() => {
    if (isOpen && colony) {
      loadCollectionPoints();
    }
  }, [isOpen, colony, loadCollectionPoints]);

  const getDirections = (point) => {
    if (point.latitude && point.longitude) {
      const url = `https://www.google.com/maps/dir/?api=1&destination=${point.latitude},${point.longitude}`;
      window.open(url, '_blank');
    }
  };

  const getWasteTypeColor = (wasteType) => {
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

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-4xl max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <MapPin className="text-emerald-600" />
            Collection Points - {colony?.colony_name}
          </h2>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <X size={24} />
          </button>
        </div>

        {loading && (
          <div className="flex justify-center py-8">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
          </div>
        )}

        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
            {error}
          </div>
        )}

        {!loading && !error && (
          <div className="space-y-4">
            {collectionPoints.length > 0 ? (
              collectionPoints.map(point => (
                <div key={point.point_id} className="border rounded-lg p-4 hover:shadow-md transition-shadow">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h3 className="text-lg font-semibold text-gray-800">{point.point_name}</h3>
                      {point.location_description && (
                        <p className="text-sm text-gray-600 mt-1">{point.location_description}</p>
                      )}
                    </div>
                    {point.latitude && point.longitude && (
                      <button
                        onClick={() => getDirections(point)}
                        className="flex items-center gap-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-md hover:bg-blue-200 transition-colors text-sm"
                      >
                        <Navigation size={14} />
                        Directions
                      </button>
                    )}
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2 flex items-center gap-1">
                        <Package size={14} />
                        Accepted Waste Types
                      </h4>
                      <div className="flex flex-wrap gap-1">
                        {point.waste_types_accepted && point.waste_types_accepted.map(type => (
                          <span
                            key={type}
                            className={`px-2 py-1 rounded-full text-xs font-medium ${getWasteTypeColor(type)}`}
                          >
                            {type.charAt(0).toUpperCase() + type.slice(1)}
                          </span>
                        ))}
                      </div>
                    </div>

                    <div>
                      <h4 className="text-sm font-medium text-gray-700 mb-2">Capacity</h4>
                      <div className="space-y-1">
                        <div className="flex justify-between text-sm">
                          <span>Current:</span>
                          <span className="font-medium">{parseFloat(point.current_capacity_kg || 0).toFixed(1)} kg</span>
                        </div>
                        <div className="flex justify-between text-sm">
                          <span>Maximum:</span>
                          <span className="font-medium">{parseFloat(point.max_capacity_kg || 0).toFixed(1)} kg</span>
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
                    </div>
                  </div>

                  {point.last_collection_date && (
                    <div className="mt-3 pt-3 border-t">
                      <p className="text-xs text-gray-500">
                        Last collection: {new Date(point.last_collection_date).toLocaleDateString()}
                      </p>
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-center py-8 text-gray-500">
                <MapPin size={48} className="mx-auto mb-4 text-gray-300" />
                <p>No collection points found for this colony.</p>
                <p className="text-sm mt-2">Collection points may need to be set up by the colony administration.</p>
              </div>
            )}
          </div>
        )}

        <div className="flex justify-end mt-6">
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-md hover:bg-gray-300 transition-colors"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
};

export default CollectionPointsModal;