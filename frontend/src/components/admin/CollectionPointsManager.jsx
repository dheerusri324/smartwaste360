// frontend/src/components/admin/CollectionPointsManager.jsx

import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, useMapEvents } from 'react-leaflet';
import { MapPin, Plus, Edit, Trash2, Save, X } from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import api from '../../services/api';

// Fix for default markers in React Leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require('leaflet/dist/images/marker-icon-2x.png'),
  iconUrl: require('leaflet/dist/images/marker-icon.png'),
  shadowUrl: require('leaflet/dist/images/marker-shadow.png'),
});

const CollectionPointsManager = () => {
  const [collectionPoints, setCollectionPoints] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showCreateForm, setShowCreateForm] = useState(false);
  const [selectedLocation, setSelectedLocation] = useState(null);
  const [editingPoint] = useState(null);
  const [mapCenter] = useState([17.385044, 78.486671]); // Hyderabad coordinates

  const [formData, setFormData] = useState({
    point_name: '',
    location_description: '',
    latitude: '',
    longitude: '',
    waste_types_accepted: [],
    max_capacity_kg: 100
  });

  const wasteTypes = [
    { value: 'plastic', label: 'Plastic', color: 'bg-blue-100 text-blue-800' },
    { value: 'paper', label: 'Paper', color: 'bg-green-100 text-green-800' },
    { value: 'metal', label: 'Metal', color: 'bg-gray-100 text-gray-800' },
    { value: 'glass', label: 'Glass', color: 'bg-purple-100 text-purple-800' },
    { value: 'organic', label: 'Organic', color: 'bg-yellow-100 text-yellow-800' },
    { value: 'textile', label: 'Textile', color: 'bg-pink-100 text-pink-800' }
  ];

  useEffect(() => {
    loadCollectionPoints();
  }, []);

  const loadCollectionPoints = async () => {
    try {
      setLoading(true);
      const response = await api.get('/admin/collection-points');
      setCollectionPoints(response.data.collection_points || []);
    } catch (error) {
      console.error('Error loading collection points:', error);
      setError('Failed to load collection points');
    } finally {
      setLoading(false);
    }
  };



  const handleMapClick = (e) => {
    if (showCreateForm) {
      const { lat, lng } = e.latlng;
      setSelectedLocation({ lat, lng });
      setFormData(prev => ({
        ...prev,
        latitude: lat.toFixed(6),
        longitude: lng.toFixed(6)
      }));
    }
  };

  const MapClickHandler = () => {
    useMapEvents({
      click: handleMapClick
    });
    return null;
  };

  const handleWasteTypeToggle = (wasteType) => {
    setFormData(prev => ({
      ...prev,
      waste_types_accepted: prev.waste_types_accepted.includes(wasteType)
        ? prev.waste_types_accepted.filter(type => type !== wasteType)
        : [...prev.waste_types_accepted, wasteType]
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.point_name || !formData.latitude || !formData.longitude || formData.waste_types_accepted.length === 0) {
      setError('Please fill in all required fields and select at least one waste type');
      return;
    }

    try {
      await api.post('/admin/collection-points', {
        ...formData,
        latitude: parseFloat(formData.latitude),
        longitude: parseFloat(formData.longitude),
        max_capacity_kg: parseFloat(formData.max_capacity_kg)
      });

      await loadCollectionPoints();
      resetForm();
      setError('');
    } catch (err) {
      console.error('Error creating collection point:', err);
      setError(err.response?.data?.error || 'Failed to create collection point');
    }
  };

  const resetForm = () => {
    setFormData({
      point_name: '',
      location_description: '',
      latitude: '',
      longitude: '',
      waste_types_accepted: [],
      max_capacity_kg: 100
    });
    setShowCreateForm(false);
    setSelectedLocation(null);
    setEditingPoint(null);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600"></div>
        <span className="ml-2">Loading collection points...</span>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex justify-between items-center">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Collection Points Management</h2>
          <p className="text-gray-600">Create and manage waste collection points</p>
        </div>
        <button
          onClick={() => setShowCreateForm(!showCreateForm)}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
        >
          {showCreateForm ? <X size={16} /> : <Plus size={16} />}
          {showCreateForm ? 'Cancel' : 'Add Collection Point'}
        </button>
      </div>

      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {/* Map */}
      <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <MapPin className="text-emerald-600" />
            Collection Points Map
            {showCreateForm && (
              <span className="text-sm font-normal text-gray-600 ml-2">
                Click on the map to select location
              </span>
            )}
          </h3>
        </div>
        
        <div style={{ height: '400px' }}>
          <MapContainer
            center={mapCenter}
            zoom={12}
            style={{ height: '100%', width: '100%' }}
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            <MapClickHandler />
            
            {/* Existing collection points */}
            {collectionPoints.map((point) => (
              <Marker
                key={point.point_id}
                position={[parseFloat(point.latitude), parseFloat(point.longitude)]}
              />
            ))}
            
            {/* Selected location for new point */}
            {selectedLocation && (
              <Marker
                position={[selectedLocation.lat, selectedLocation.lng]}
                icon={L.icon({
                  iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                  iconSize: [25, 41],
                  iconAnchor: [12, 41],
                  popupAnchor: [1, -34],
                  shadowSize: [41, 41]
                })}
              />
            )}
          </MapContainer>
        </div>
      </div>

      {/* Create Form */}
      {showCreateForm && (
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">Create New Collection Point</h3>
          
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Point Name *
                </label>
                <input
                  type="text"
                  value={formData.point_name}
                  onChange={(e) => setFormData(prev => ({ ...prev, point_name: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="e.g., Central Park Collection Point"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Max Capacity (kg)
                </label>
                <input
                  type="number"
                  value={formData.max_capacity_kg}
                  onChange={(e) => setFormData(prev => ({ ...prev, max_capacity_kg: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  min="1"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Location Description
              </label>
              <input
                type="text"
                value={formData.location_description}
                onChange={(e) => setFormData(prev => ({ ...prev, location_description: e.target.value }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                placeholder="e.g., Near main entrance, next to parking area"
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Latitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.latitude}
                  onChange={(e) => setFormData(prev => ({ ...prev, latitude: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="Click on map to select"
                  required
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Longitude *
                </label>
                <input
                  type="number"
                  step="any"
                  value={formData.longitude}
                  onChange={(e) => setFormData(prev => ({ ...prev, longitude: e.target.value }))}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="Click on map to select"
                  required
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Accepted Waste Types *
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                {wasteTypes.map(type => (
                  <label key={type.value} className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.waste_types_accepted.includes(type.value)}
                      onChange={() => handleWasteTypeToggle(type.value)}
                      className="rounded border-gray-300 text-emerald-600 focus:ring-emerald-500"
                    />
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${type.color}`}>
                      {type.label}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            <div className="flex gap-4 pt-4">
              <button
                type="submit"
                className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 transition-colors"
              >
                <Save size={16} />
                Create Collection Point
              </button>
              
              <button
                type="button"
                onClick={resetForm}
                className="flex items-center gap-2 px-6 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
              >
                <X size={16} />
                Cancel
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Collection Points List */}
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-4 border-b">
          <h3 className="text-lg font-semibold text-gray-800">
            Existing Collection Points ({collectionPoints.length})
          </h3>
        </div>
        
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Point Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Location
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Waste Types
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Capacity
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {collectionPoints.map((point) => (
                <tr key={point.point_id}>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="text-sm font-medium text-gray-900">{point.point_name}</div>
                    <div className="text-sm text-gray-500">{point.location_description}</div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {parseFloat(point.latitude).toFixed(4)}, {parseFloat(point.longitude).toFixed(4)}
                  </td>
                  <td className="px-6 py-4">
                    <div className="flex flex-wrap gap-1">
                      {point.waste_types_accepted && point.waste_types_accepted.map((type) => {
                        const wasteType = wasteTypes.find(wt => wt.value === type);
                        return (
                          <span
                            key={type}
                            className={`px-2 py-1 rounded-full text-xs font-medium ${wasteType?.color || 'bg-gray-100 text-gray-800'}`}
                          >
                            {wasteType?.label || type}
                          </span>
                        );
                      })}
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                    {point.max_capacity_kg} kg
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className={`px-2 py-1 rounded-full text-xs font-medium ${
                      point.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {point.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                    <div className="flex gap-2">
                      <button
                        onClick={() => setEditingPoint(point)}
                        className="text-emerald-600 hover:text-emerald-900"
                      >
                        <Edit size={16} />
                      </button>
                      <button
                        onClick={() => {/* Add delete functionality */}}
                        className="text-red-600 hover:text-red-900"
                      >
                        <Trash2 size={16} />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          
          {collectionPoints.length === 0 && (
            <div className="text-center py-12">
              <MapPin className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900">No collection points</h3>
              <p className="mt-1 text-sm text-gray-500">Get started by creating a new collection point.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CollectionPointsManager;