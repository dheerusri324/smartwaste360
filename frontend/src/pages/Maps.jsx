// frontend/src/pages/Maps.jsx

import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { getUserLocation } from '../services/user';
import { getNearbyColonies } from '../services/colonies';
import { getReadyColonies } from '../services/collector'; // Import collector service
import { useCollectorLocation } from '../hooks/useCollectorLocation';
import ColonyMap from '../components/maps/ColonyMap';
import NearbyColonies from '../components/maps/NearbyColonies';
import SimpleCollectionPointsMap from '../components/maps/SimpleCollectionPointsMap';
import { MapPin, Building, Package, Navigation, Globe, Target } from 'lucide-react';

const Maps = () => {
  const { user } = useAuth();
  const [userLocation, setUserLocation] = useState(null);
  const [locationLoading, setLocationLoading] = useState(true);
  const [locationError, setLocationError] = useState(null);
  const [colonies, setColonies] = useState([]);
  const [loadingColonies, setLoadingColonies] = useState(true);
  const [activeTab, setActiveTab] = useState('colonies'); // 'colonies' or 'collection-points'

  const isCollector = user?.role === 'collector';
  
  // Use different location strategies for collectors vs users
  const collectorLocation = useCollectorLocation();
  
  const effectiveLocation = isCollector ? collectorLocation.location : userLocation;
  const effectiveLocationLoading = isCollector ? collectorLocation.loading : locationLoading;
  const effectiveLocationError = isCollector ? collectorLocation.error : locationError;

  const mapTitle = isCollector ? "Available Pickups" : "Nearby Colonies";
  
  const getMapDescription = () => {
    if (isCollector) {
      if (collectorLocation.isShowingAll) {
        return "Showing all colonies ready for collection (no location filter).";
      } else if (collectorLocation.isUsingCurrentLocation) {
        return "Showing colonies ready for collection near your current location.";
      } else if (collectorLocation.isUsingCustomLocation) {
        return `Showing colonies ready for collection near ${effectiveLocation?.name || 'your selected area'}.`;
      }
      return "Showing colonies ready for collection.";
    } else {
      return `Showing colonies within 25km of your registered location${userLocation ? ` (${userLocation.colony_name})` : ''}.`;
    }
  };

  // Get user's registered location (for regular users, not collectors)
  useEffect(() => {
    const loadUserLocation = async () => {
      if (user && !isCollector && user.role !== 'admin') {
        try {
          setLocationLoading(true);
          const location = await getUserLocation();
          if (location) {
            setUserLocation(location);
            console.log('User location loaded:', location);
          } else {
            setLocationError('Could not determine your location from your profile');
          }
        } catch (error) {
          console.error('Failed to load user location:', error);
          setLocationError('Failed to load your location');
        } finally {
          setLocationLoading(false);
        }
      } else if (user && user.role === 'admin') {
        // For admin users, use a default location (Hyderabad city center)
        setUserLocation({
          lat: 17.385044,
          lng: 78.486671,
          colony_name: 'Admin View',
          colony_id: null
        });
        setLocationLoading(false);
        console.log('Admin user - using default location');
      } else {
        // No user or unknown role
        setLocationLoading(false);
      }
    };

    loadUserLocation();
  }, [user, isCollector]);

  const fetchMapData = useCallback(async () => {
    try {
      setLoadingColonies(true);
      let data;
      
      if (isCollector) {
        // Collector logic: ready colonies with optional location filter
        console.log('Fetching ready colonies for collector, location:', effectiveLocation);
        console.log('Location method:', collectorLocation.locationMethod);
        
        // Check if "Show All" is selected (locationMethod === 'all')
        if (collectorLocation.locationMethod === 'all') {
          // Show all colonies without location filter
          console.log('Showing all colonies (no location filter)');
          data = await getReadyColonies(null);
        } else {
          // Add radius parameter for collectors with location
          const locationWithRadius = effectiveLocation ? {
            ...effectiveLocation,
            radius: 500 // 500km radius for collectors
          } : null;
          
          data = await getReadyColonies(locationWithRadius);
        }
        console.log('Ready colonies data:', data);
      } else if (userLocation) {
        // User logic: nearby colonies within 25km of registered location
        console.log('Fetching nearby colonies for user location:', userLocation);
        data = await getNearbyColonies(userLocation.lat, userLocation.lng, 25);
        console.log('Nearby colonies data:', data);
      } else {
        // No location available for users
        setColonies([]);
        setLoadingColonies(false);
        return;
      }
      
      setColonies(data.colonies || []);
    } catch (err) {
      console.error("Failed to load map data:", err);
      if (isCollector) {
        setLocationError('Failed to load available pickups');
      } else {
        setLocationError('Failed to load nearby colonies');
      }
    } finally {
      setLoadingColonies(false);
    }
  }, [userLocation, effectiveLocation, isCollector, collectorLocation.locationMethod]);

  useEffect(() => {
    fetchMapData();
  }, [fetchMapData]);

  if (effectiveLocationLoading && !isCollector) {
    return <div className="p-6">Getting your location...</div>;
  }
  
  const mapCenter = effectiveLocation ? [effectiveLocation.lat, effectiveLocation.lng] : [17.3850, 78.4867];

  const getCollectionPointsFilters = () => {
    const filters = {};
    
    // For collectors, use their location logic
    if (isCollector && effectiveLocation) {
      filters.latitude = effectiveLocation.lat;
      filters.longitude = effectiveLocation.lng;
      filters.radius = 25;
    }
    // For regular users, use their location if available, otherwise show all
    else if (!isCollector && userLocation) {
      filters.latitude = userLocation.lat;
      filters.longitude = userLocation.lng;
      filters.radius = 25;
    }
    // If no location available, return empty filters to show all collection points
    
    return filters;
  };

  return (
    <div className="p-6 space-y-6">
      {/* Tab Navigation */}
      <div className="bg-white rounded-lg shadow-sm border p-1 flex">
        <button
          onClick={() => setActiveTab('colonies')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-colors ${
            activeTab === 'colonies'
              ? 'bg-emerald-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Building size={16} />
          {isCollector ? 'Ready Colonies' : 'Nearby Colonies'}
        </button>
        <button
          onClick={() => setActiveTab('collection-points')}
          className={`flex-1 flex items-center justify-center gap-2 px-4 py-2 rounded-md transition-colors ${
            activeTab === 'collection-points'
              ? 'bg-emerald-600 text-white'
              : 'text-gray-600 hover:bg-gray-100'
          }`}
        >
          <Package size={16} />
          Collection Points
        </button>
      </div>

      {/* Collector Location Controls */}
      {isCollector && (
        <div className="bg-white rounded-lg shadow-sm border p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3 flex items-center gap-2">
            <Target size={16} />
            Location Filter
          </h3>
          <div className="flex flex-wrap gap-2">
            {collectorLocation.savedLocation && (
              <button
                onClick={collectorLocation.loadSavedLocation}
                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  collectorLocation.isUsingSavedLocation
                    ? 'bg-emerald-100 text-emerald-700 border border-emerald-300'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                <MapPin size={14} />
                Saved Location
              </button>
            )}
            
            <button
              onClick={collectorLocation.getCurrentLocation}
              disabled={collectorLocation.loading}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                collectorLocation.isUsingCurrentLocation
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Navigation size={14} />
              {collectorLocation.loading ? 'Getting Location...' : 'Current Location'}
            </button>
            
            <button
              onClick={collectorLocation.showAllColonies}
              className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                collectorLocation.isShowingAll
                  ? 'bg-gray-100 text-gray-700 border border-gray-300'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              <Globe size={14} />
              Show All
            </button>
          </div>
          
          {effectiveLocationError && (
            <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-700">
              {effectiveLocationError}
            </div>
          )}
          
          {effectiveLocation && (
            <div className="mt-3 text-xs text-gray-500">
              {collectorLocation.isUsingSavedLocation && (
                <>📍 Using your saved location ({effectiveLocation.city || 'Unknown area'})</>
              )}
              {collectorLocation.isUsingCurrentLocation && (
                <>📍 Using your current location (±{Math.round(effectiveLocation.accuracy || 0)}m accuracy)</>
              )}
              {collectorLocation.isUsingCustomLocation && (
                <>📍 Using {effectiveLocation.name}</>
              )}
            </div>
          )}
          
          {!effectiveLocation && !collectorLocation.loading && collectorLocation.locationMethod !== 'all' && (
            <div className="mt-3 p-2 bg-yellow-50 border border-yellow-200 rounded text-sm">
              <p className="text-yellow-700">
                No location set. <a href="/collector/settings" className="underline font-medium">Add your location in settings</a> for better pickup recommendations.
              </p>
            </div>
          )}
        </div>
      )}

      {/* Content based on active tab */}
      {activeTab === 'colonies' ? (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6 h-[calc(100vh-200px)]">
          <div className="md:col-span-3 h-full rounded-lg overflow-hidden shadow-lg">
            {locationError && <p className="text-center text-red-500 p-4">{locationError}</p>}
            <ColonyMap center={mapCenter} colonies={colonies} userLocation={userLocation} isCollector={isCollector} />
          </div>
          <div className="md:col-span-1 h-full overflow-y-auto bg-white p-4 rounded-lg shadow-lg">
            <h2 className="text-xl font-bold mb-1">{mapTitle}</h2>
            <p className="text-sm text-gray-500 mb-4">{getMapDescription()}</p>
            <NearbyColonies colonies={colonies} loading={loadingColonies} isCollector={isCollector} />
          </div>
        </div>
      ) : (
        <div className="h-[calc(100vh-200px)] overflow-y-auto">
          <SimpleCollectionPointsMap filters={getCollectionPointsFilters()} />
        </div>
      )}
    </div>
  );
};

export default Maps;