// frontend/src/pages/CollectorSettings.jsx

import React, { useState, useEffect } from 'react';
import { getCollectorProfile, updateCollectorProfile, updateCollectorLocation } from '../services/collector';
import { MapPin, Save, Navigation, Globe, User, Truck } from 'lucide-react';

const CollectorSettings = () => {
  const [profile, setProfile] = useState(null);
  const [location, setLocation] = useState({
    latitude: '',
    longitude: '',
    address: '',
    city: '',
    state: '',
    pincode: '',
    service_radius_km: 50
  });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      setLoading(true);
      const response = await getCollectorProfile();
      const collectorData = response.collector;
      setProfile(collectorData);
      
      // Set location data if available
      if (collectorData.latitude && collectorData.longitude) {
        setLocation({
          latitude: collectorData.latitude || '',
          longitude: collectorData.longitude || '',
          address: collectorData.address || '',
          city: collectorData.city || '',
          state: collectorData.state || '',
          pincode: collectorData.pincode || '',
          service_radius_km: collectorData.service_radius_km || 50
        });
      }
    } catch (err) {
      setError('Failed to load profile');
    } finally {
      setLoading(false);
    }
  };

  const getCurrentLocation = () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser');
      return;
    }

    setMessage('Getting your current location...');
    navigator.geolocation.getCurrentPosition(
      (position) => {
        setLocation(prev => ({
          ...prev,
          latitude: position.coords.latitude.toString(),
          longitude: position.coords.longitude.toString()
        }));
        setMessage('Location detected! Please add address details and save.');
      },
      (error) => {
        setError(`Location error: ${error.message}`);
        setMessage('');
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 300000
      }
    );
  };

  const handleLocationChange = (field, value) => {
    setLocation(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const saveLocation = async () => {
    if (!location.latitude || !location.longitude) {
      setError('Latitude and longitude are required');
      return;
    }

    try {
      setSaving(true);
      setError('');
      
      const locationData = {
        latitude: parseFloat(location.latitude),
        longitude: parseFloat(location.longitude),
        address: location.address,
        city: location.city,
        state: location.state,
        pincode: location.pincode,
        service_radius_km: parseFloat(location.service_radius_km)
      };

      await updateCollectorLocation(locationData);
      setMessage('Location saved successfully!');
      
      // Reload profile to get updated data
      await loadProfile();
      
    } catch (err) {
      setError('Failed to save location: ' + (err.message || 'Unknown error'));
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-emerald-600 mx-auto"></div>
        <p className="text-center mt-2">Loading settings...</p>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-4xl mx-auto">
      <div className="bg-white rounded-lg shadow-sm border">
        <div className="p-6 border-b">
          <h1 className="text-2xl font-bold text-gray-800 flex items-center gap-2">
            <User className="text-emerald-600" />
            Collector Settings
          </h1>
          <p className="text-gray-600 mt-1">Manage your profile and service location</p>
        </div>

        <div className="p-6 space-y-6">
          {/* Profile Info */}
          <div className="bg-gray-50 p-4 rounded-lg">
            <h3 className="font-semibold text-gray-800 mb-2 flex items-center gap-2">
              <Truck size={16} />
              Profile Information
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <span className="font-medium">Name:</span> {profile?.name}
              </div>
              <div>
                <span className="font-medium">Email:</span> {profile?.email}
              </div>
              <div>
                <span className="font-medium">Phone:</span> {profile?.phone}
              </div>
              <div>
                <span className="font-medium">Vehicle:</span> {profile?.vehicle_number || 'Not set'}
              </div>
            </div>
          </div>

          {/* Location Settings */}
          <div>
            <h3 className="text-lg font-semibold text-gray-800 mb-4 flex items-center gap-2">
              <MapPin className="text-emerald-600" />
              Service Location Settings
            </h3>
            <p className="text-gray-600 mb-4">
              Set your service location to help the system show you relevant pickup opportunities in your area.
            </p>

            <div className="space-y-4">
              {/* Current Location Button */}
              <div className="flex gap-2">
                <button
                  onClick={getCurrentLocation}
                  className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  <Navigation size={16} />
                  Use Current Location
                </button>
                <button
                  onClick={() => window.open('https://www.google.com/maps', '_blank')}
                  className="flex items-center gap-2 px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition-colors"
                >
                  <Globe size={16} />
                  Open Google Maps
                </button>
              </div>

              {/* Coordinates */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Latitude *
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={location.latitude}
                    onChange={(e) => handleLocationChange('latitude', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="e.g., 17.3850"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Longitude *
                  </label>
                  <input
                    type="number"
                    step="any"
                    value={location.longitude}
                    onChange={(e) => handleLocationChange('longitude', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="e.g., 78.4867"
                  />
                </div>
              </div>

              {/* Address Details */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Address
                </label>
                <textarea
                  value={location.address}
                  onChange={(e) => handleLocationChange('address', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  rows="2"
                  placeholder="Your service area address"
                />
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    City
                  </label>
                  <input
                    type="text"
                    value={location.city}
                    onChange={(e) => handleLocationChange('city', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="City"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    State
                  </label>
                  <input
                    type="text"
                    value={location.state}
                    onChange={(e) => handleLocationChange('state', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="State"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Pincode
                  </label>
                  <input
                    type="text"
                    value={location.pincode}
                    onChange={(e) => handleLocationChange('pincode', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                    placeholder="Pincode"
                  />
                </div>
              </div>

              {/* Service Radius */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Service Radius (km)
                </label>
                <input
                  type="number"
                  min="1"
                  max="500"
                  value={location.service_radius_km}
                  onChange={(e) => handleLocationChange('service_radius_km', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-emerald-500"
                  placeholder="50"
                />
                <p className="text-xs text-gray-500 mt-1">
                  Maximum distance you're willing to travel for pickups
                </p>
              </div>

              {/* Save Button */}
              <div className="flex gap-4 pt-4">
                <button
                  onClick={saveLocation}
                  disabled={saving || !location.latitude || !location.longitude}
                  className="flex items-center gap-2 px-6 py-2 bg-emerald-600 text-white rounded-lg hover:bg-emerald-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
                >
                  <Save size={16} />
                  {saving ? 'Saving...' : 'Save Location'}
                </button>
              </div>
            </div>
          </div>

          {/* Messages */}
          {message && (
            <div className="bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded">
              {message}
            </div>
          )}

          {error && (
            <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded">
              {error}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CollectorSettings;